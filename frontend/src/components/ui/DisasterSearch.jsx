import React from 'react';
import algoliasearch from 'algoliasearch/lite';
import {
  InstantSearch,
  useSearchBox,
  useHits,
  Highlight,
} from 'react-instantsearch-hooks-web';

import { Card } from './card.jsx';
import { Badge } from './badge.jsx';
import { MapPin, ShieldAlert, Users, AlertTriangle, Search } from 'lucide-react';
import { Input } from './input.jsx';

// ✅ Use Vite environment variables
const searchClient = algoliasearch(
  import.meta.env.VITE_ALGOLIA_APP_ID,
  import.meta.env.VITE_ALGOLIA_SEARCH_KEY
);

// Single result card
const Hit = ({ hit }) => {
  const severity = hit.severity || 'medium';
  const color = hit.color || 'yellow';
  const time = hit.disaster_type || 'Unknown time';
  const area = hit.location || 'Unknown area';
  const affected = hit.population_affected || 'Unknown';

  return (
    <Card className="p-4 space-y-3">
      <div className="flex items-start justify-between">
        <div className="flex items-center gap-2">
          <AlertTriangle className={`h-5 w-5 text-${color}-600`} />
          <Badge variant={severity === 'high' ? 'destructive' : 'secondary'}>
            {severity.toUpperCase()}
          </Badge>
        </div>
        <div className="flex items-center gap-1 text-sm text-muted-foreground">
          <ShieldAlert className="h-4 w-4" />
          {time}
        </div>
      </div>

      <div className="space-y-2">
        <h3 className="text-lg font-semibold">
          <Highlight attribute="title" hit={hit} />
        </h3>
        <div className="flex items-center gap-4 text-sm text-muted-foreground">
          <div className="flex items-center gap-1">
            <MapPin className="h-4 w-4" />
            {area}
          </div>
          <div className="flex items-center gap-1">
            <Users className="h-4 w-4" />
            {affected}
          </div>
        </div>
        <p className="text-sm">
          <Highlight attribute="description" hit={hit} />
        </p>
      </div>
    </Card>
  );
};

// Hits component
const Hits = () => {
  const { hits } = useHits();

  return (
    <div className="flex flex-col gap-4 mt-4">
      {hits.map((hit) => (
        <Hit key={hit.objectID} hit={hit} />
      ))}
    </div>
  );
};

// Search input
const SearchBox = () => {
  const { query, refine } = useSearchBox();

  return (
    <div className="relative w-full">
      <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-muted-foreground" />
      <Input
        className="pl-10 h-12 w-full"
        type="search"
        placeholder="Search for specific help..."
        value={query}
        onChange={(e) => refine(e.target.value)}
      />
    </div>
  );
};

// Main Search Component
export function DisasterSearch() {
  return (
    <InstantSearch
      searchClient={searchClient}
      indexName={import.meta.env.VITE_DISASTER_INDEX_NAME}
    >
      <div className="w-full px-4 py-6 space-y-6">
        <h2 className="text-2xl font-bold text-center sm:text-left">
          Search Disaster Alerts
        </h2>

        <SearchBox />

        <Hits />
      </div>
    </InstantSearch>
  );
}
