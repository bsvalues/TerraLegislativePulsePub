import React from 'react';
import { Card, List, Tag, Typography, Button, Space, Progress, Tooltip } from 'antd';
import { 
  ToolOutlined, 
  CheckCircleOutlined, 
  ClockCircleOutlined,
  DollarOutlined,
  CalendarOutlined
} from '@ant-design/icons';
import { PropertyImprovement } from '../types/property';

const { Title, Text } = Typography;

interface PropertyImprovementsProps {
  improvements: PropertyImprovement[];
  onAddImprovement: () => void;
  onEditImprovement: (improvement: PropertyImprovement) => void;
  onDeleteImprovement: (improvement: PropertyImprovement) => void;
}

const PropertyImprovements: React.FC<PropertyImprovementsProps> = ({
  improvements,
  onAddImprovement,
  onEditImprovement,
  onDeleteImprovement
}) => {
  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(value);
  };

  const formatDate = (date: string) => {
    return new Date(date).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'success';
      case 'in_progress':
        return 'processing';
      case 'planned':
        return 'warning';
      default:
        return 'default';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircleOutlined />;
      case 'in_progress':
        return <ClockCircleOutlined />;
      case 'planned':
        return <ToolOutlined />;
      default:
        return null;
    }
  };

  const calculateProgress = (improvements: PropertyImprovement[]) => {
    const total = improvements.length;
    const completed = improvements.filter(i => i.status === 'completed').length;
    return Math.round((completed / total) * 100);
  };

  return (
    <Card
      title={
        <Space>
          <Title level={4}>Property Improvements</Title>
          <Button type="primary" onClick={onAddImprovement}>
            Add Improvement
          </Button>
        </Space>
      }
    >
      <div className="improvements-summary">
        <Progress
          percent={calculateProgress(improvements)}
          status="active"
          format={percent => `${percent}% Complete`}
        />
      </div>

      <List
        dataSource={improvements}
        renderItem={improvement => (
          <List.Item
            actions={[
              <Button type="link" onClick={() => onEditImprovement(improvement)}>
                Edit
              </Button>,
              <Button type="link" danger onClick={() => onDeleteImprovement(improvement)}>
                Delete
              </Button>
            ]}
          >
            <List.Item.Meta
              avatar={
                <Tooltip title={improvement.status}>
                  <Tag color={getStatusColor(improvement.status)} icon={getStatusIcon(improvement.status)}>
                    {improvement.status.toUpperCase()}
                  </Tag>
                </Tooltip>
              }
              title={improvement.type}
              description={
                <Space direction="vertical" size="small">
                  <Text>{improvement.description}</Text>
                  <Space>
                    <DollarOutlined />
                    <Text strong>{formatCurrency(improvement.value)}</Text>
                    <CalendarOutlined />
                    <Text type="secondary">{formatDate(improvement.date)}</Text>
                  </Space>
                </Space>
              }
            />
          </List.Item>
        )}
      />
    </Card>
  );
};

export default PropertyImprovements; 