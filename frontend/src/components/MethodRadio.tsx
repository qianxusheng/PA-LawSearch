import React from 'react';
import { SearchMethod } from '@/types';

interface MethodRadioProps {
  value: SearchMethod;
  label: string;
  checked: boolean;
  disabled: boolean;
  onChange: (value: SearchMethod) => void;
}

const MethodRadio: React.FC<MethodRadioProps> = ({ value, label, checked, disabled, onChange }) => (
  <label className="flex items-center gap-2 cursor-pointer">
    <input
      type="radio"
      name="method"
      value={value}
      checked={checked}
      onChange={() => onChange(value)}
      disabled={disabled}
      className="w-4 h-4 text-indigo-600 cursor-pointer"
    />
    <span className="text-sm font-medium text-gray-700">{label}</span>
  </label>
);

export default MethodRadio;
