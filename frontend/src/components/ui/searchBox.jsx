import React from 'react';
import { useSearchBox } from 'react-instantsearch-dom';
import { Search } from 'lucide-react';
import { Input } from './input'; // your styled input component

export function CustomSearchBox() {
  const { query, refine } = useSearchBox();

  return (
    <div className="relative w-full max-w-3xl mx-auto">
      <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-muted-foreground" />
      <Input
        placeholder="Search for specific help..."
        value={query}
        onChange={(e) => refine(e.currentTarget.value)}
        className="pl-10 h-12"
      />
    </div>
  );
}
