import React from 'react';
import { Home, AlertTriangle, MapPin, Route, Shield, MessageCircle } from 'lucide-react';

export function Navigation({ currentPage, onNavigate }) {
  const navItems = [
    { id: 'home', icon: Home, label: 'Home' },
    { id: 'dashboard', icon: AlertTriangle, label: 'Alerts' },
    { id: 'relief', icon: MapPin, label: 'Relief' },
    //{ id: 'route', icon: Route, label: 'Route' },
    { id: 'safety', icon: Shield, label: 'Safety' },
    { id: 'chat', icon: MessageCircle, label: 'Ask AI' },
  ];

  return (
    <nav className="fixed bottom-0 left-1/2 transform -translate-x-1/2 w-full max-w-lg bg-white border-t border-border">
      <div className="grid grid-cols-5 h-20">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = currentPage === item.id;
          
          return (
            <button
              key={item.id}
              onClick={() => onNavigate(item.id)}
              className={`flex flex-col items-center justify-center gap-1 transition-colors ${
                isActive 
                  ? 'text-primary bg-primary/5' 
                  : 'text-muted-foreground hover:text-foreground'
              }`}
            >
              <Icon size={24} strokeWidth={2} />
              <span className="text-xs">{item.label}</span>
            </button>
          );
        })}
      </div>
    </nav>
  );
}