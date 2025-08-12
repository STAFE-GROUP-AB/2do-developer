#!/usr/bin/env python3
"""
Agent Heartbeat Service for 2DO CLI
Maintains agent presence in the network and handles cleanup
"""

import time
import threading
import signal
import sys
from typing import Optional

from .agent_registry import AgentRegistry
from .agent_communicator import AgentCommunicator
from .config import ConfigManager


class AgentHeartbeatService:
    """Background service to maintain agent presence"""
    
    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager
        self.agent_registry = AgentRegistry(config_manager)
        self.agent_communicator = AgentCommunicator(config_manager, self.agent_registry)
        
        self.heartbeat_interval = 30  # seconds
        self.cleanup_interval = 60   # seconds
        self.running = False
        self.heartbeat_thread = None
        self.cleanup_thread = None
        
        # Register signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def start(self, agent_name: Optional[str] = None) -> None:
        """Start the heartbeat service"""
        if self.running:
            return
        
        # Register the agent
        self.agent_registry.register_agent(agent_name)
        
        self.running = True
        
        # Start heartbeat thread
        self.heartbeat_thread = threading.Thread(target=self._heartbeat_loop, daemon=True)
        self.heartbeat_thread.start()
        
        # Start cleanup thread
        self.cleanup_thread = threading.Thread(target=self._cleanup_loop, daemon=True)
        self.cleanup_thread.start()
    
    def stop(self) -> None:
        """Stop the heartbeat service and cleanup"""
        if not self.running:
            return
        
        self.running = False
        
        # Unregister the agent
        self.agent_registry.unregister_agent()
        
        # Wait for threads to finish
        if self.heartbeat_thread and self.heartbeat_thread.is_alive():
            self.heartbeat_thread.join(timeout=1)
        
        if self.cleanup_thread and self.cleanup_thread.is_alive():
            self.cleanup_thread.join(timeout=1)
    
    def _heartbeat_loop(self) -> None:
        """Main heartbeat loop"""
        while self.running:
            try:
                # Update heartbeat timestamp
                self.agent_registry.update_heartbeat()
                
                # Sleep for heartbeat interval
                for _ in range(self.heartbeat_interval):
                    if not self.running:
                        break
                    time.sleep(1)
                    
            except Exception:
                # Ignore heartbeat errors, continue trying
                time.sleep(5)
    
    def _cleanup_loop(self) -> None:
        """Cleanup loop for registry and messages"""
        while self.running:
            try:
                # Clean up stale agent entries
                self.agent_registry.cleanup_registry()
                
                # Clean up old messages
                self.agent_communicator.cleanup_old_messages()
                
                # Sleep for cleanup interval
                for _ in range(self.cleanup_interval):
                    if not self.running:
                        break
                    time.sleep(1)
                    
            except Exception:
                # Ignore cleanup errors, continue trying
                time.sleep(10)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        self.stop()
        sys.exit(0)
    
    def is_running(self) -> bool:
        """Check if the service is running"""
        return self.running
    
    def get_status(self) -> dict:
        """Get service status information"""
        online_agents = self.agent_registry.get_online_agents()
        collaborations = self.agent_communicator.get_active_collaborations()
        
        return {
            'running': self.running,
            'agent_id': self.agent_registry.agent_id if hasattr(self.agent_registry, 'agent_id') else None,
            'online_agents_count': len(online_agents),
            'active_collaborations': len(collaborations),
            'heartbeat_interval': self.heartbeat_interval,
            'cleanup_interval': self.cleanup_interval
        }


# Global heartbeat service instance
_heartbeat_service: Optional[AgentHeartbeatService] = None


def start_agent_heartbeat(config_manager: ConfigManager, agent_name: Optional[str] = None) -> AgentHeartbeatService:
    """Start the global agent heartbeat service"""
    global _heartbeat_service
    
    if _heartbeat_service is None:
        _heartbeat_service = AgentHeartbeatService(config_manager)
    
    _heartbeat_service.start(agent_name)
    return _heartbeat_service


def stop_agent_heartbeat() -> None:
    """Stop the global agent heartbeat service"""
    global _heartbeat_service
    
    if _heartbeat_service is not None:
        _heartbeat_service.stop()


def get_agent_heartbeat_service() -> Optional[AgentHeartbeatService]:
    """Get the current heartbeat service instance"""
    return _heartbeat_service


def is_agent_heartbeat_running() -> bool:
    """Check if agent heartbeat is running"""
    return _heartbeat_service is not None and _heartbeat_service.is_running()