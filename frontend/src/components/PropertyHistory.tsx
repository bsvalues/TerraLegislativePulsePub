import React from 'react';
import { Timeline, Card, Typography, Tag, Space, Button } from 'antd';
import { ClockCircleOutlined, DollarOutlined, UserOutlined } from '@ant-design/icons';
import { PropertyHistory as PropertyHistoryType } from '../types/property';

const { Title, Text } = Typography;

interface PropertyHistoryProps {
  history: PropertyHistoryType[];
  onExport?: () => void;
}

const PropertyHistory: React.FC<PropertyHistoryProps> = ({
  history,
  onExport
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
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getActionColor = (action: string) => {
    switch (action.toLowerCase()) {
      case 'assessment':
        return 'blue';
      case 'sale':
        return 'green';
      case 'tax payment':
        return 'purple';
      case 'improvement':
        return 'orange';
      default:
        return 'default';
    }
  };

  return (
    <Card
      title={
        <Space>
          <Title level={4}>Property History</Title>
          {onExport && (
            <Button type="primary" onClick={onExport}>
              Export History
            </Button>
          )}
        </Space>
      }
    >
      <Timeline mode="left">
        {history.map((item, index) => (
          <Timeline.Item
            key={index}
            dot={<ClockCircleOutlined style={{ fontSize: '16px' }} />}
            color={getActionColor(item.action)}
          >
            <Card size="small" className="history-item-card">
              <Space direction="vertical" size="small">
                <div className="history-header">
                  <Tag color={getActionColor(item.action)}>
                    {item.action.toUpperCase()}
                  </Tag>
                  <Text type="secondary">{formatDate(item.date)}</Text>
                </div>

                <div className="history-details">
                  <Space>
                    <DollarOutlined />
                    <Text strong>{formatCurrency(item.value)}</Text>
                  </Space>
                  <Space>
                    <UserOutlined />
                    <Text type="secondary">User ID: {item.userId}</Text>
                  </Space>
                </div>

                {item.notes && (
                  <div className="history-notes">
                    <Text type="secondary">{item.notes}</Text>
                  </div>
                )}
              </Space>
            </Card>
          </Timeline.Item>
        ))}
      </Timeline>
    </Card>
  );
};

export default PropertyHistory; 