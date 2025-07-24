import React from 'react';
import { Button } from './ui/button.jsx';
import { Card } from './ui/card.jsx';
import { Alert, AlertDescription } from './ui/alert.jsx';
import { MapPin, Phone, AlertTriangle, MessageCircle } from 'lucide-react';

export function HomeScreen({ onNavigate }) {
  return (
    <div className="p-6 pb-24 space-y-6">
      {/* Header */}
      <div className="text-center space-y-2">
        <h1 className="text-3xl text-primary">Relief Finder AI</h1>
        <p className="">Find help when you need it most</p>
      </div>

      {/* Current Status Alert */}
      <Alert className="border-amber-200 bg-amber-50">
        <AlertTriangle className="h-5 w-5 text-amber-600" />
        <AlertDescription className="text-amber-800">
          <strong>Weather Alert:</strong> Heavy rain warning for your area. Stay safe indoors.
        </AlertDescription>
      </Alert>

      {/* Main Action Button */}
      <Card className="p-6 text-center space-y-4">
        <div className="space-y-2">
          <h2 className="text-xl">Need Help Right Now?</h2>
          <p className="text-muted-foreground">Find nearby shelters, food, and medical aid</p>
        </div>
        <Button 
          onClick={() => onNavigate('relief')} 
          size="lg" 
          className="w-full h-14 text-lg"
        >
          <MapPin className="mr-2 h-6 w-6" />
          Find Help Near Me
        </Button>
      </Card>

      {/* Emergency Contact */}
      <Card className="p-6 bg-red-50 border-red-200">
        <div className="text-center space-y-3">
          <h3 className="text-red-800">Emergency Contact</h3>
          <Button 
            variant="destructive" 
            size="lg" 
            className="w-full h-14 text-lg"
            onClick={() => window.open('tel:334-9241133')}
          >
            <Phone className="mr-2 h-6 w-6" />
            Call Disaster Team
          </Button>
        </div>
      </Card>

      {/* Quick Actions */}
      <div className="grid grid-cols-2 gap-4">
        <Button 
          variant="outline" 
          size="lg" 
          className="h-16 flex-col gap-2"
          onClick={() => onNavigate('dashboard')}
        >
          <AlertTriangle className="h-6 w-6" />
          View Alerts
        </Button>
        <Button 
          variant="outline" 
          size="lg" 
          className="h-16 flex-col gap-2"
          onClick={() => onNavigate('chat')}
        >
          <MessageCircle className="h-6 w-6" />
          Ask AI
        </Button>
      </div>
    </div>
  );
}