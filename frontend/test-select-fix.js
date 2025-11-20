// Quick test to verify the Select component fix
import React from 'react';
import { Select, SelectTrigger, SelectContent, SelectItem, SelectValue } from './src/components/ui/select';

// Test component to verify no DOM prop warnings
function TestSelect() {
  const [value, setValue] = React.useState('');

  return (
    <Select value={value} onValueChange={setValue}>
      <SelectTrigger>
        <SelectValue placeholder="Select an option" />
      </SelectTrigger>
      <SelectContent>
        <SelectItem value="option1">Option 1</SelectItem>
        <SelectItem value="option2">Option 2</SelectItem>
        <SelectItem value="option3">Option 3</SelectItem>
      </SelectContent>
    </Select>
  );
}

export default TestSelect;
