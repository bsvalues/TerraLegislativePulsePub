import React from 'react';
import { Form, Input, InputNumber, DatePicker, Select, Button, Space, message } from 'antd';
import { useForm } from 'antd/lib/form/Form';
import { PropertyType, PropertyStatus } from '../types/property';

const { Option } = Select;

interface PropertyFormProps {
  initialValues?: any;
  onSubmit: (values: any) => Promise<void>;
  onCancel: () => void;
}

const PropertyForm: React.FC<PropertyFormProps> = ({
  initialValues,
  onSubmit,
  onCancel
}) => {
  const [form] = useForm();
  const [loading, setLoading] = React.useState(false);

  const handleSubmit = async (values: any) => {
    try {
      setLoading(true);
      await onSubmit(values);
      message.success('Property information saved successfully');
      form.resetFields();
    } catch (error) {
      message.error('Failed to save property information');
      console.error('Form submission error:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Form
      form={form}
      layout="vertical"
      initialValues={initialValues}
      onFinish={handleSubmit}
      requiredMark={false}
    >
      <Form.Item
        name="address"
        label="Property Address"
        rules={[
          { required: true, message: 'Please enter the property address' },
          { min: 5, message: 'Address must be at least 5 characters long' }
        ]}
      >
        <Input placeholder="Enter property address" />
      </Form.Item>

      <Form.Item
        name="type"
        label="Property Type"
        rules={[{ required: true, message: 'Please select property type' }]}
      >
        <Select placeholder="Select property type">
          {Object.values(PropertyType).map(type => (
            <Option key={type} value={type}>{type}</Option>
          ))}
        </Select>
      </Form.Item>

      <Form.Item
        name="status"
        label="Status"
        rules={[{ required: true, message: 'Please select property status' }]}
      >
        <Select placeholder="Select property status">
          {Object.values(PropertyStatus).map(status => (
            <Option key={status} value={status}>{status}</Option>
          ))}
        </Select>
      </Form.Item>

      <Form.Item
        name="value"
        label="Property Value"
        rules={[
          { required: true, message: 'Please enter property value' },
          { type: 'number', min: 0, message: 'Value must be positive' }
        ]}
      >
        <InputNumber
          style={{ width: '100%' }}
          formatter={value => `$ ${value}`.replace(/\B(?=(\d{3})+(?!\d))/g, ',')}
          parser={value => value!.replace(/\$\s?|(,*)/g, '')}
          placeholder="Enter property value"
        />
      </Form.Item>

      <Form.Item
        name="area"
        label="Property Area (sq ft)"
        rules={[
          { required: true, message: 'Please enter property area' },
          { type: 'number', min: 0, message: 'Area must be positive' }
        ]}
      >
        <InputNumber
          style={{ width: '100%' }}
          formatter={value => `${value} sq ft`}
          parser={value => value!.replace(' sq ft', '')}
          placeholder="Enter property area"
        />
      </Form.Item>

      <Form.Item
        name="owner"
        label="Property Owner"
        rules={[
          { required: true, message: 'Please enter property owner' },
          { min: 2, message: 'Owner name must be at least 2 characters long' }
        ]}
      >
        <Input placeholder="Enter property owner name" />
      </Form.Item>

      <Form.Item
        name="lastAssessment"
        label="Last Assessment Date"
        rules={[{ required: true, message: 'Please select last assessment date' }]}
      >
        <DatePicker style={{ width: '100%' }} />
      </Form.Item>

      <Form.Item
        name="description"
        label="Description"
        rules={[{ max: 500, message: 'Description cannot exceed 500 characters' }]}
      >
        <Input.TextArea
          rows={4}
          placeholder="Enter property description"
          showCount
          maxLength={500}
        />
      </Form.Item>

      <Form.Item>
        <Space>
          <Button type="primary" htmlType="submit" loading={loading}>
            Save Property
          </Button>
          <Button onClick={onCancel}>
            Cancel
          </Button>
        </Space>
      </Form.Item>
    </Form>
  );
};

export default PropertyForm; 