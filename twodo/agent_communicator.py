#!/usr/bin/env python3
"""
Agent Communication System for 2DO CLI
Enables agents to send messages, request help, and collaborate with each other.
"""

import json
import os
import time
import uuid
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum

from .agent_registry import AgentRegistry, AgentInfo
from .config import ConfigManager


class MessageType(Enum):
    """Types of messages agents can send"""
    HELP_REQUEST = "help_request"
    HELP_OFFER = "help_offer"
    HELP_ACCEPTED = "help_accepted"
    HELP_DECLINED = "help_declined"
    COLLABORATION_START = "collaboration_start"
    COLLABORATION_MESSAGE = "collaboration_message"
    COLLABORATION_END = "collaboration_end"
    PING = "ping"
    PONG = "pong"
    STATUS_UPDATE = "status_update"


@dataclass
class Message:
    """Inter-agent message"""
    message_id: str
    from_agent_id: str
    to_agent_id: str
    message_type: MessageType
    content: Dict[str, Any]
    timestamp: float
    expires_at: Optional[float] = None
    reply_to: Optional[str] = None


@dataclass
class HelpRequest:
    """Request for help from another agent"""
    request_id: str
    title: str
    description: str
    required_capabilities: List[str]
    tech_stack: List[str]
    priority: str  # low, medium, high, urgent
    estimated_effort: str  # quick, moderate, significant
    repository_context: str


@dataclass
class CollaborationSession:
    """Active collaboration between two agents"""
    session_id: str
    helper_agent_id: str
    requester_agent_id: str
    help_request: HelpRequest
    started_at: float
    last_activity: float
    status: str  # active, paused, completed, cancelled
    messages: List[Dict[str, Any]]


class AgentCommunicator:
    """Handles inter-agent communication and collaboration"""
    
    def __init__(self, config_manager: ConfigManager, agent_registry: AgentRegistry):
        self.config_manager = config_manager
        self.agent_registry = agent_registry
        
        self.messages_dir = Path.home() / ".2do" / "messages"
        self.messages_dir.mkdir(parents=True, exist_ok=True)
        
        self.collaboration_dir = Path.home() / ".2do" / "collaborations"
        self.collaboration_dir.mkdir(parents=True, exist_ok=True)
        
        self.message_timeout = 300  # 5 minutes for message expiry
        self.collaboration_timeout = 3600  # 1 hour for collaboration inactivity
        
    def send_message(self, to_agent_id: str, message_type: MessageType, 
                    content: Dict[str, Any], reply_to: Optional[str] = None,
                    expires_in: Optional[int] = None) -> str:
        """Send a message to another agent"""
        message_id = str(uuid.uuid4())
        expires_at = None
        if expires_in:
            expires_at = time.time() + expires_in
        
        message = Message(
            message_id=message_id,
            from_agent_id=self.agent_registry.agent_id,
            to_agent_id=to_agent_id,
            message_type=message_type,
            content=content,
            timestamp=time.time(),
            expires_at=expires_at,
            reply_to=reply_to
        )
        
        # Save message in recipient's inbox
        inbox_dir = self.messages_dir / to_agent_id
        inbox_dir.mkdir(exist_ok=True)
        
        message_file = inbox_dir / f"{message_id}.json"
        with open(message_file, 'w') as f:
            # Convert enum to string for JSON serialization
            message_dict = asdict(message)
            message_dict['message_type'] = message_type.value
            json.dump(message_dict, f, indent=2)
        
        return message_id
    
    def get_messages(self, message_types: Optional[List[MessageType]] = None) -> List[Message]:
        """Get messages for this agent"""
        inbox_dir = self.messages_dir / self.agent_registry.agent_id
        if not inbox_dir.exists():
            return []
        
        messages = []
        current_time = time.time()
        
        for message_file in inbox_dir.glob("*.json"):
            try:
                with open(message_file, 'r') as f:
                    data = json.load(f)
                
                # Check if message has expired
                if data.get('expires_at') and current_time > data['expires_at']:
                    message_file.unlink()
                    continue
                
                # Convert string back to enum
                message_type = MessageType(data['message_type'])
                
                # Filter by message types if specified
                if message_types and message_type not in message_types:
                    continue
                
                message = Message(
                    message_id=data['message_id'],
                    from_agent_id=data['from_agent_id'],
                    to_agent_id=data['to_agent_id'],
                    message_type=message_type,
                    content=data['content'],
                    timestamp=data['timestamp'],
                    expires_at=data.get('expires_at'),
                    reply_to=data.get('reply_to')
                )
                messages.append(message)
                
            except Exception:
                # Remove corrupted message files
                try:
                    message_file.unlink()
                except Exception:
                    pass
        
        # Sort by timestamp (newest first)
        messages.sort(key=lambda m: m.timestamp, reverse=True)
        return messages
    
    def mark_message_read(self, message_id: str) -> None:
        """Mark a message as read (delete it)"""
        inbox_dir = self.messages_dir / self.agent_registry.agent_id
        message_file = inbox_dir / f"{message_id}.json"
        try:
            if message_file.exists():
                message_file.unlink()
        except Exception:
            pass
    
    def send_help_request(self, title: str, description: str, 
                         required_capabilities: List[str], tech_stack: List[str],
                         priority: str = "medium", estimated_effort: str = "moderate") -> str:
        """Send a help request to available agents"""
        # Get repository context
        repo_info = self.agent_registry._get_repo_info()
        
        help_request = HelpRequest(
            request_id=str(uuid.uuid4()),
            title=title,
            description=description,
            required_capabilities=required_capabilities,
            tech_stack=tech_stack,
            priority=priority,
            estimated_effort=estimated_effort,
            repository_context=repo_info['readme_summary']
        )
        
        # Find potential helper agents
        potential_helpers = []
        for capability in required_capabilities:
            potential_helpers.extend(
                self.agent_registry.find_agents_with_capability(capability)
            )
        
        for tech in tech_stack:
            potential_helpers.extend(
                self.agent_registry.find_agents_with_tech_stack(tech)
            )
        
        # Remove duplicates and get unique agents
        unique_helpers = {agent.agent_id: agent for agent in potential_helpers}
        
        if not unique_helpers:
            # Broadcast to all online agents if no specific matches
            unique_helpers = {agent.agent_id: agent for agent in self.agent_registry.get_online_agents()}
        
        # Send help request messages
        messages_sent = 0
        for agent in unique_helpers.values():
            content = {
                'help_request': asdict(help_request),
                'requester_info': {
                    'repo_name': repo_info['repo_name'],
                    'repo_path': repo_info['repo_path'],
                    'tech_stack': repo_info['tech_stack'],
                    'github_url': repo_info.get('github_url')
                }
            }
            
            self.send_message(
                to_agent_id=agent.agent_id,
                message_type=MessageType.HELP_REQUEST,
                content=content,
                expires_in=self.message_timeout
            )
            messages_sent += 1
        
        return help_request.request_id
    
    def send_help_offer(self, help_request_message: Message, offer_message: str) -> str:
        """Offer help for a help request"""
        content = {
            'request_id': help_request_message.content['help_request']['request_id'],
            'offer_message': offer_message,
            'helper_info': {
                'capabilities': self.agent_registry._get_repo_info()['capabilities'],
                'tech_stack': self.agent_registry._get_repo_info()['tech_stack'],
                'repo_name': self.agent_registry._get_repo_info()['repo_name'],
                'experience': self._analyze_experience(help_request_message.content['help_request'])
            }
        }
        
        return self.send_message(
            to_agent_id=help_request_message.from_agent_id,
            message_type=MessageType.HELP_OFFER,
            content=content,
            reply_to=help_request_message.message_id,
            expires_in=self.message_timeout
        )
    
    def accept_help_offer(self, help_offer_message: Message) -> str:
        """Accept a help offer and start collaboration"""
        # Start collaboration session
        session_id = self._start_collaboration_session(
            helper_agent_id=help_offer_message.from_agent_id,
            help_request_id=help_offer_message.content['request_id']
        )
        
        content = {
            'session_id': session_id,
            'request_id': help_offer_message.content['request_id'],
            'acceptance_message': "Let's work together on this!"
        }
        
        return self.send_message(
            to_agent_id=help_offer_message.from_agent_id,
            message_type=MessageType.HELP_ACCEPTED,
            content=content,
            reply_to=help_offer_message.message_id
        )
    
    def decline_help_offer(self, help_offer_message: Message, reason: str = "") -> str:
        """Decline a help offer"""
        content = {
            'request_id': help_offer_message.content['request_id'],
            'decline_reason': reason
        }
        
        return self.send_message(
            to_agent_id=help_offer_message.from_agent_id,
            message_type=MessageType.HELP_DECLINED,
            content=content,
            reply_to=help_offer_message.message_id
        )
    
    def _start_collaboration_session(self, helper_agent_id: str, help_request_id: str) -> str:
        """Start a new collaboration session"""
        session_id = str(uuid.uuid4())
        
        # Create collaboration session data structure
        session = CollaborationSession(
            session_id=session_id,
            helper_agent_id=helper_agent_id,
            requester_agent_id=self.agent_registry.agent_id,
            help_request=HelpRequest(
                request_id=help_request_id,
                title="",  # Will be filled from actual request
                description="",
                required_capabilities=[],
                tech_stack=[],
                priority="medium",
                estimated_effort="moderate",
                repository_context=""
            ),
            started_at=time.time(),
            last_activity=time.time(),
            status="active",
            messages=[]
        )
        
        # Save collaboration session
        session_file = self.collaboration_dir / f"{session_id}.json"
        with open(session_file, 'w') as f:
            json.dump(asdict(session), f, indent=2)
        
        # Update agent status
        self.agent_registry.update_agent_status("collaborating")
        
        return session_id
    
    def send_collaboration_message(self, session_id: str, message: str, 
                                 message_type: str = "chat") -> str:
        """Send a message in an active collaboration session"""
        # Load collaboration session
        session = self._load_collaboration_session(session_id)
        if not session:
            raise ValueError(f"Collaboration session {session_id} not found")
        
        # Determine recipient
        if session.requester_agent_id == self.agent_registry.agent_id:
            recipient = session.helper_agent_id
        else:
            recipient = session.requester_agent_id
        
        # Send message
        content = {
            'session_id': session_id,
            'message': message,
            'message_type': message_type,  # chat, code, question, guidance, etc.
            'timestamp': time.time()
        }
        
        message_id = self.send_message(
            to_agent_id=recipient,
            message_type=MessageType.COLLABORATION_MESSAGE,
            content=content
        )
        
        # Update collaboration session
        session.messages.append(content)
        session.last_activity = time.time()
        self._save_collaboration_session(session)
        
        return message_id
    
    def _load_collaboration_session(self, session_id: str) -> Optional[CollaborationSession]:
        """Load collaboration session from disk"""
        session_file = self.collaboration_dir / f"{session_id}.json"
        if session_file.exists():
            try:
                with open(session_file, 'r') as f:
                    data = json.load(f)
                return CollaborationSession(**data)
            except Exception:
                return None
        return None
    
    def _save_collaboration_session(self, session: CollaborationSession) -> None:
        """Save collaboration session to disk"""
        session_file = self.collaboration_dir / f"{session.session_id}.json"
        with open(session_file, 'w') as f:
            json.dump(asdict(session), f, indent=2)
    
    def get_active_collaborations(self) -> List[CollaborationSession]:
        """Get all active collaboration sessions for this agent"""
        collaborations = []
        current_time = time.time()
        
        for session_file in self.collaboration_dir.glob("*.json"):
            try:
                session = self._load_collaboration_session(session_file.stem)
                if not session:
                    continue
                
                # Check if this agent is involved
                if (session.requester_agent_id != self.agent_registry.agent_id and 
                    session.helper_agent_id != self.agent_registry.agent_id):
                    continue
                
                # Check if session is still active
                if (session.status == "active" and 
                    current_time - session.last_activity <= self.collaboration_timeout):
                    collaborations.append(session)
                elif current_time - session.last_activity > self.collaboration_timeout:
                    # Mark as timed out
                    session.status = "timed_out"
                    self._save_collaboration_session(session)
                
            except Exception:
                continue
        
        return collaborations
    
    def end_collaboration(self, session_id: str, reason: str = "completed") -> None:
        """End a collaboration session"""
        session = self._load_collaboration_session(session_id)
        if session:
            session.status = reason
            session.last_activity = time.time()
            self._save_collaboration_session(session)
            
            # Notify the other agent
            if session.requester_agent_id == self.agent_registry.agent_id:
                recipient = session.helper_agent_id
            else:
                recipient = session.requester_agent_id
            
            content = {
                'session_id': session_id,
                'end_reason': reason,
                'final_message': f"Collaboration ended: {reason}"
            }
            
            self.send_message(
                to_agent_id=recipient,
                message_type=MessageType.COLLABORATION_END,
                content=content
            )
            
            # Update agent status back to available
            self.agent_registry.update_agent_status("available")
    
    def _analyze_experience(self, help_request: Dict[str, Any]) -> str:
        """Analyze this agent's experience relevant to the help request"""
        repo_info = self.agent_registry._get_repo_info()
        my_capabilities = repo_info['capabilities']
        my_tech_stack = repo_info['tech_stack']
        
        requested_capabilities = help_request.get('required_capabilities', [])
        requested_tech = help_request.get('tech_stack', [])
        
        # Calculate experience score
        capability_matches = len(set(my_capabilities) & set(requested_capabilities))
        tech_matches = len(set(my_tech_stack) & set(requested_tech))
        
        total_requested = len(requested_capabilities) + len(requested_tech)
        total_matches = capability_matches + tech_matches
        
        if total_requested == 0:
            return "general development experience"
        
        experience_ratio = total_matches / total_requested
        
        if experience_ratio >= 0.8:
            return "expert level experience"
        elif experience_ratio >= 0.6:
            return "strong experience"
        elif experience_ratio >= 0.4:
            return "moderate experience"
        elif experience_ratio >= 0.2:
            return "some experience"
        else:
            return "limited experience but willing to help"
    
    def cleanup_old_messages(self) -> None:
        """Clean up expired messages and old collaborations"""
        current_time = time.time()
        
        # Clean up messages
        inbox_dir = self.messages_dir / self.agent_registry.agent_id
        if inbox_dir.exists():
            for message_file in inbox_dir.glob("*.json"):
                try:
                    with open(message_file, 'r') as f:
                        data = json.load(f)
                    
                    if data.get('expires_at') and current_time > data['expires_at']:
                        message_file.unlink()
                        
                except Exception:
                    try:
                        message_file.unlink()
                    except Exception:
                        pass
        
        # Clean up old collaborations
        for session_file in self.collaboration_dir.glob("*.json"):
            try:
                session = self._load_collaboration_session(session_file.stem)
                if (session and session.status in ["completed", "cancelled", "timed_out"] and
                    current_time - session.last_activity > 86400):  # 24 hours
                    session_file.unlink()
            except Exception:
                pass