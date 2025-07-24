import React, { useState } from 'react';
import { Card } from './ui/card.jsx';
import { Button } from './ui/button.jsx';
import { Badge } from './ui/badge.jsx';
import { MapPin, Navigation, Clock, AlertTriangle, Car, Footprints } from 'lucide-react';

export function RoutePlanner() {
  const [selectedDestination, setSelectedDestination] = useState(null);

  const destinations = [
    {
      id: 1,
      name: 'Community Center Shelter',
      address: '123 Main St',
      distance: '0.3 miles',
      driveTime: '2 min',
      walkTime: '6 min',
      safetyLevel: 'high',
      routeStatus: 'clear',
      warnings: []
    },
    {
      id: 2,
      name: 'Red Cross Food Station',
      address: '456 Oak Ave',
      distance: '0.7 miles',
      driveTime: '3 min',
      walkTime: '14 min',
      safetyLevel: 'medium',
      routeStatus: 'caution',
      warnings: ['Flooded intersection at Oak & 2nd']
    },
    {
      id: 3,
      name: 'Mobile Medical Unit',
      address: 'City Park - North Entrance',
      distance: '1.2 miles',
      driveTime: '5 min',
      walkTime: '24 min',
      safetyLevel: 'high',
      routeStatus: 'clear',
      warnings: []
    }
  ];

  const getSafetyColor = (level) => {
    switch (level) {
      case 'high': return 'green';
      case 'medium': return 'yellow';
      case 'low': return 'red';
      default: return 'gray';
    }
  };

  const getRouteColor = (status) => {
    switch (status) {
      case 'clear': return 'green';
      case 'caution': return 'yellow';
      case 'blocked': return 'red';
      default: return 'gray';
    }
  };

  return (
    <div className="p-6 pb-24 space-y-6">
      {/* Header */}
      <div className="text-center space-y-2">
        <h1 className="text-2xl">Route Planner</h1>
        <p className="">Safe routes to help locations</p>
      </div>

      {/* Current Location */}
      <Card className="p-4 bg-blue-50 border-blue-200">
        <div className="flex items-center gap-3">
          <div className="w-3 h-3 bg-blue-600 rounded-full animate-pulse"></div>
          <div>
            <p className="text-sm text-blue-800">Your Current Location</p>
            <p className="text-blue-900">789 Elm Street, Your City</p>
          </div>
        </div>
      </Card>

      {/* Route Options */}
      <div className="space-y-4">
        <h2 className="text-xl">Choose Destination</h2>
        {destinations.map((destination) => (
          <Card key={destination.id} className="p-4 space-y-4">
            <div className="flex items-start justify-between">
              <div className="space-y-1">
                <h3 className="text-lg">{destination.name}</h3>
                <p className="text-sm text-muted-foreground">{destination.address}</p>
              </div>
              <div className="text-right">
                <Badge 
                  variant="outline" 
                  className={`border-${getSafetyColor(destination.safetyLevel)}-500 text-${getSafetyColor(destination.safetyLevel)}-700`}
                >
                  {destination.safetyLevel.toUpperCase()} SAFETY
                </Badge>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4 p-3 bg-muted/50 rounded-lg">
              <div className="flex items-center gap-2">
                <Car className="h-5 w-5 text-muted-foreground" />
                <div>
                  <p className="text-sm">Drive</p>
                  <p className="text-xs text-muted-foreground">{destination.driveTime}</p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <Footprints className="h-5 w-5 text-muted-foreground" />
                <div>
                  <p className="text-sm">Walk</p>
                  <p className="text-xs text-muted-foreground">{destination.walkTime}</p>
                </div>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <Badge 
                variant="outline" 
                className={`border-${getRouteColor(destination.routeStatus)}-500 text-${getRouteColor(destination.routeStatus)}-700`}
              >
                Route {destination.routeStatus.toUpperCase()}
              </Badge>
              <span className="text-sm text-muted-foreground">{destination.distance}</span>
            </div>

            {destination.warnings.length > 0 && (
              <div className="space-y-2">
                {destination.warnings.map((warning, index) => (
                  <div key={index} className="flex items-start gap-2 p-2 bg-yellow-50 border border-yellow-200 rounded">
                    <AlertTriangle className="h-4 w-4 text-yellow-600 mt-0.5 flex-shrink-0" />
                    <p className="text-sm text-yellow-800">{warning}</p>
                  </div>
                ))}
              </div>
            )}

            <div className="grid grid-cols-2 gap-2">
              <Button 
                variant="outline" 
                size="sm"
                onClick={() => setSelectedDestination(destination.id)}
              >
                <MapPin className="mr-1 h-4 w-4" />
                View Route
              </Button>
              <Button size="sm">
                <Navigation className="mr-1 h-4 w-4" />
                Start Navigation
              </Button>
            </div>
          </Card>
        ))}
      </div>

      {/* Map Placeholder */}
      {selectedDestination && (
        <Card className="p-6 bg-slate-100 h-64 flex items-center justify-center">
          <div className="text-center space-y-2">
            <Navigation className="h-12 w-12 mx-auto text-muted-foreground" />
            <p className="text-muted-foreground">Interactive Route Map</p>
            <p className="text-sm text-muted-foreground">Turn-by-turn directions with hazard warnings</p>
          </div>
        </Card>
      )}

      {/* Emergency Note */}
      <Card className="p-4 bg-red-50 border-red-200">
        <div className="flex items-start gap-3">
          <AlertTriangle className="h-5 w-5 text-red-600 mt-0.5" />
          <div className="space-y-1">
            <p className="text-red-800">Safety Reminder</p>
            <p className="text-sm text-red-700">
              Routes are updated every 15 minutes. Conditions may change rapidly during disasters. 
              Use your best judgment and turn back if you encounter danger.
            </p>
          </div>
        </div>
      </Card>
    </div>
  );
}