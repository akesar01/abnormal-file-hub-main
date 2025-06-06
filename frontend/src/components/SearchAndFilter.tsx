import React, { useState } from 'react';
import { MagnifyingGlassIcon, FunnelIcon, XMarkIcon } from '@heroicons/react/24/outline';
import { FileFilters } from '../services/fileService';

interface SearchAndFilterProps {
  onFiltersChange: (filters: FileFilters) => void;
  fileTypes: string[];
}

export const SearchAndFilter: React.FC<SearchAndFilterProps> = ({ onFiltersChange, fileTypes }) => {
  const [search, setSearch] = useState('');
  const [fileType, setFileType] = useState('');
  const [minSize, setMinSize] = useState('');
  const [maxSize, setMaxSize] = useState('');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [ordering, setOrdering] = useState('-uploaded_at');
  const [showAdvanced, setShowAdvanced] = useState(false);

  const handleApplyFilters = () => {
    const filters: FileFilters = {
      search: search || undefined,
      file_type: fileType || undefined,
      min_size: minSize ? parseInt(minSize) : undefined,
      max_size: maxSize ? parseInt(maxSize) : undefined,
      start_date: startDate || undefined,
      end_date: endDate || undefined,
      ordering,
    };
    onFiltersChange(filters);
  };

  const handleClearFilters = () => {
    setSearch('');
    setFileType('');
    setMinSize('');
    setMaxSize('');
    setStartDate('');
    setEndDate('');
    setOrdering('-uploaded_at');
    onFiltersChange({});
  };

  const hasActiveFilters = search || fileType || minSize || maxSize || startDate || endDate;

  return (
    <div className="bg-white shadow sm:rounded-lg p-6 mb-6">
      <div className="space-y-4">
        {/* Search Bar */}
        <div className="flex gap-2">
          <div className="flex-1">
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <MagnifyingGlassIcon className="h-5 w-5 text-gray-400" />
              </div>
              <input
                type="text"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleApplyFilters()}
                className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md leading-5 bg-white placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-1 focus:ring-primary-500 focus:border-primary-500"
                placeholder="Search by filename..."
              />
            </div>
          </div>
          <button
            onClick={() => setShowAdvanced(!showAdvanced)}
            className="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
          >
            <FunnelIcon className="h-5 w-5 mr-2" />
            Filters
            {hasActiveFilters && (
              <span className="ml-2 inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-primary-100 text-primary-800">
                Active
              </span>
            )}
          </button>
          <button
            onClick={handleApplyFilters}
            className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
          >
            Search
          </button>
        </div>

        {/* Advanced Filters */}
        {showAdvanced && (
          <div className="border-t pt-4 space-y-4">
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {/* File Type Filter */}
              <div>
                <label htmlFor="file-type" className="block text-sm font-medium text-gray-700">
                  File Type
                </label>
                <select
                  id="file-type"
                  value={fileType}
                  onChange={(e) => setFileType(e.target.value)}
                  className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm rounded-md"
                >
                  <option value="">All types</option>
                  {fileTypes.map((type) => (
                    <option key={type} value={type}>
                      {type}
                    </option>
                  ))}
                </select>
              </div>

              {/* Size Range */}
              <div>
                <label className="block text-sm font-medium text-gray-700">Size Range (bytes)</label>
                <div className="mt-1 flex gap-2">
                  <input
                    type="number"
                    value={minSize}
                    onChange={(e) => setMinSize(e.target.value)}
                    placeholder="Min"
                    className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
                  />
                  <span className="py-2">-</span>
                  <input
                    type="number"
                    value={maxSize}
                    onChange={(e) => setMaxSize(e.target.value)}
                    placeholder="Max"
                    className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
                  />
                </div>
              </div>

              {/* Upload Date Range */}
              <div>
                <label className="block text-sm font-medium text-gray-700">Upload Date Range</label>
                <div className="mt-1 flex gap-2">
                  <input
                    type="date"
                    value={startDate}
                    onChange={(e) => setStartDate(e.target.value)}
                    className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
                  />
                  <span className="py-2">-</span>
                  <input
                    type="date"
                    value={endDate}
                    onChange={(e) => setEndDate(e.target.value)}
                    className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
                  />
                </div>
              </div>

              {/* Sort By */}
              <div>
                <label htmlFor="sort-by" className="block text-sm font-medium text-gray-700">
                  Sort By
                </label>
                <select
                  id="sort-by"
                  value={ordering}
                  onChange={(e) => setOrdering(e.target.value)}
                  className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm rounded-md"
                >
                  <option value="-uploaded_at">Newest First</option>
                  <option value="uploaded_at">Oldest First</option>
                  <option value="-size">Largest First</option>
                  <option value="size">Smallest First</option>
                  <option value="original_filename">Name (A-Z)</option>
                  <option value="-original_filename">Name (Z-A)</option>
                </select>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex justify-end gap-2 pt-2">
              <button
                onClick={handleClearFilters}
                disabled={!hasActiveFilters}
                className="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <XMarkIcon className="h-4 w-4 mr-2" />
                Clear Filters
              </button>
              <button
                onClick={handleApplyFilters}
                className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
              >
                Apply Filters
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}; 