import React from 'react';
import { Card, Descriptions, Typography, Button, Space, Progress, Tag } from 'antd';
import { 
  DollarOutlined, 
  CalendarOutlined, 
  FileTextOutlined,
  CheckCircleOutlined,
  ClockCircleOutlined
} from '@ant-design/icons';
import { Property } from '../types/property';

const { Title, Text } = Typography;

interface PropertyTaxInfoProps {
  property: Property;
  onViewTaxHistory: () => void;
  onMakePayment: () => void;
  onDownloadTaxStatement: () => void;
}

const PropertyTaxInfo: React.FC<PropertyTaxInfoProps> = ({
  property,
  onViewTaxHistory,
  onMakePayment,
  onDownloadTaxStatement
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

  const calculateTaxAmount = (value: number, rate: number) => {
    return value * (rate / 100);
  };

  const getPaymentStatus = (lastPayment: string, nextPayment: string) => {
    const now = new Date();
    const next = new Date(nextPayment);
    const last = new Date(lastPayment);

    if (now > next) {
      return {
        status: 'overdue',
        color: 'error',
        text: 'Payment Overdue'
      };
    } else if (now > last && now < next) {
      return {
        status: 'current',
        color: 'success',
        text: 'Payment Current'
      };
    } else {
      return {
        status: 'upcoming',
        color: 'warning',
        text: 'Payment Upcoming'
      };
    }
  };

  if (!property.taxInfo) {
    return (
      <Card>
        <Title level={4}>Tax Information</Title>
        <Text type="secondary">No tax information available for this property.</Text>
      </Card>
    );
  }

  const { taxId, taxRate, lastPayment, nextPayment } = property.taxInfo;
  const taxAmount = calculateTaxAmount(property.value, taxRate);
  const paymentStatus = getPaymentStatus(lastPayment, nextPayment);

  return (
    <Card
      title={
        <Space>
          <Title level={4}>Tax Information</Title>
          <Tag color={paymentStatus.color} icon={
            paymentStatus.status === 'current' ? <CheckCircleOutlined /> : <ClockCircleOutlined />
          }>
            {paymentStatus.text}
          </Tag>
        </Space>
      }
    >
      <Descriptions bordered column={2}>
        <Descriptions.Item label="Tax ID" span={2}>
          {taxId}
        </Descriptions.Item>
        <Descriptions.Item label="Property Value">
          {formatCurrency(property.value)}
        </Descriptions.Item>
        <Descriptions.Item label="Tax Rate">
          {taxRate}%
        </Descriptions.Item>
        <Descriptions.Item label="Annual Tax Amount">
          {formatCurrency(taxAmount)}
        </Descriptions.Item>
        <Descriptions.Item label="Monthly Tax Amount">
          {formatCurrency(taxAmount / 12)}
        </Descriptions.Item>
        <Descriptions.Item label="Last Payment">
          {formatDate(lastPayment)}
        </Descriptions.Item>
        <Descriptions.Item label="Next Payment Due">
          {formatDate(nextPayment)}
        </Descriptions.Item>
      </Descriptions>

      <div className="tax-actions" style={{ marginTop: 16 }}>
        <Space>
          <Button 
            type="primary" 
            icon={<DollarOutlined />}
            onClick={onMakePayment}
          >
            Make Payment
          </Button>
          <Button 
            icon={<CalendarOutlined />}
            onClick={onViewTaxHistory}
          >
            View Tax History
          </Button>
          <Button 
            icon={<FileTextOutlined />}
            onClick={onDownloadTaxStatement}
          >
            Download Tax Statement
          </Button>
        </Space>
      </div>

      <div className="payment-progress" style={{ marginTop: 16 }}>
        <Text type="secondary">Payment Progress</Text>
        <Progress
          percent={paymentStatus.status === 'current' ? 100 : 0}
          status={paymentStatus.status === 'overdue' ? 'exception' : 'active'}
          format={percent => `${percent}% Paid`}
        />
      </div>
    </Card>
  );
};

export default PropertyTaxInfo; 