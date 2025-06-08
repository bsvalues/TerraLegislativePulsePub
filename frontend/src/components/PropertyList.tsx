import React from 'react';
import { List, Card, Input, Select, DatePicker, Space, Button, Row, Col } from 'antd';
import { SearchOutlined, FilterOutlined, SortAscendingOutlined } from '@ant-design/icons';
import PropertyCard from './PropertyCard';
import { Property, PropertyFilter, PropertySort, PropertyType, PropertyStatus } from '../types/property';

const { RangePicker } = DatePicker;
const { Option } = Select;

interface PropertyListProps {
  properties: Property[];
  onEdit: (id: string) => void;
  onViewHistory: (id: string) => void;
  onViewDocuments: (id: string) => void;
  onFilter: (filter: PropertyFilter) => void;
  onSort: (sort: PropertySort) => void;
  loading?: boolean;
}

const PropertyList: React.FC<PropertyListProps> = ({
  properties,
  onEdit,
  onViewHistory,
  onViewDocuments,
  onFilter,
  onSort,
  loading = false
}) => {
  const [filters, setFilters] = React.useState<PropertyFilter>({});
  const [sort, setSort] = React.useState<PropertySort>({ field: 'lastAssessment', order: 'descend' });

  const handleFilterChange = (key: keyof PropertyFilter, value: any) => {
    const newFilters = { ...filters, [key]: value };
    setFilters(newFilters);
    onFilter(newFilters);
  };

  const handleSortChange = (field: keyof Property) => {
    const newOrder = sort.field === field && sort.order === 'ascend' ? 'descend' : 'ascend';
    const newSort = { field, order: newOrder };
    setSort(newSort);
    onSort(newSort);
  };

  return (
    <div className="property-list">
      <Card className="filter-card">
        <Row gutter={[16, 16]}>
          <Col xs={24} sm={12} md={6}>
            <Input
              placeholder="Search by address or owner"
              prefix={<SearchOutlined />}
              onChange={e => handleFilterChange('owner', e.target.value)}
            />
          </Col>
          <Col xs={24} sm={12} md={6}>
            <Select
              placeholder="Property Type"
              style={{ width: '100%' }}
              onChange={value => handleFilterChange('type', value)}
            >
              {Object.values(PropertyType).map(type => (
                <Option key={type} value={type}>{type}</Option>
              ))}
            </Select>
          </Col>
          <Col xs={24} sm={12} md={6}>
            <Select
              placeholder="Status"
              style={{ width: '100%' }}
              onChange={value => handleFilterChange('status', value)}
            >
              {Object.values(PropertyStatus).map(status => (
                <Option key={status} value={status}>{status}</Option>
              ))}
            </Select>
          </Col>
          <Col xs={24} sm={12} md={6}>
            <RangePicker
              style={{ width: '100%' }}
              onChange={dates => handleFilterChange('dateRange', {
                start: dates?.[0]?.toISOString(),
                end: dates?.[1]?.toISOString()
              })}
            />
          </Col>
        </Row>
      </Card>

      <List
        grid={{
          gutter: 16,
          xs: 1,
          sm: 2,
          md: 3,
          lg: 3,
          xl: 4,
          xxl: 4,
        }}
        dataSource={properties}
        loading={loading}
        renderItem={property => (
          <List.Item>
            <PropertyCard
              property={property}
              onEdit={onEdit}
              onViewHistory={onViewHistory}
              onViewDocuments={onViewDocuments}
            />
          </List.Item>
        )}
      />
    </div>
  );
};

export default PropertyList; 