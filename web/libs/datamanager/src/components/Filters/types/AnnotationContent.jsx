import React, { useState, useEffect, useMemo } from "react";
import { observer } from "mobx-react";
import { FilterInput } from "../FilterInput";
import { FilterDropdown } from "../FilterDropdown";

// Hook to fetch annotation options from the API
function useAnnotationOptions(projectId) {
  const [options, setOptions] = useState({
    labels: {},
    choices: {},
    annotation_types: [],
    from_names: []
  });
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!projectId) return;

    setLoading(true);
    fetch(`/api/dm/annotation-options/?project=${projectId}`)
      .then(response => response.json())
      .then(data => {
        setOptions(data);
      })
      .catch(error => {
        console.error('Failed to fetch annotation options:', error);
      })
      .finally(() => {
        setLoading(false);
      });
  }, [projectId]);

  return { options, loading };
}

// Component for filtering by annotation labels
const AnnotationLabelInput = observer(({ value, onChange, projectId }) => {
  const { options, loading } = useAnnotationOptions(projectId);
  
  const allLabels = useMemo(() => {
    const labels = [];
    Object.entries(options.labels || {}).forEach(([type, labelList]) => {
      labelList.forEach(label => {
        labels.push({ value: label, label: `${label} (${type})` });
      });
    });
    return labels;
  }, [options.labels]);

  if (loading) {
    return <FilterInput type="text" value={value} onChange={onChange} placeholder="Loading..." disabled />;
  }

  return (
    <FilterDropdown
      items={allLabels}
      value={value}
      onChange={onChange}
      placeholder="Select label"
      searchable
    />
  );
});

// Component for filtering by annotation choices
const AnnotationChoiceInput = observer(({ value, onChange, projectId }) => {
  const { options, loading } = useAnnotationOptions(projectId);
  const [selectedFromName, setSelectedFromName] = useState(value?.from_name || '');
  
  const choiceOptions = useMemo(() => {
    if (!selectedFromName) {
      // Show all choices from all controls
      const allChoices = [];
      Object.entries(options.choices || {}).forEach(([fromName, choices]) => {
        choices.forEach(choice => {
          allChoices.push({ 
            value: choice, 
            label: `${choice} (${fromName})`,
            fromName 
          });
        });
      });
      return allChoices;
    } else {
      // Show only choices for selected control
      const choices = options.choices[selectedFromName] || [];
      return choices.map(choice => ({ value: choice, label: choice }));
    }
  }, [options.choices, selectedFromName]);

  const handleChoiceChange = (choiceValue) => {
    const selectedChoice = choiceOptions.find(c => c.value === choiceValue);
    onChange({
      choice: choiceValue,
      from_name: selectedChoice?.fromName || selectedFromName
    });
  };

  const handleFromNameChange = (fromName) => {
    setSelectedFromName(fromName);
    onChange({
      choice: value?.choice || '',
      from_name: fromName
    });
  };

  if (loading) {
    return <FilterInput type="text" value={value?.choice || ''} onChange={onChange} placeholder="Loading..." disabled />;
  }

  return (
    <div style={{ display: 'flex', gap: '8px', flexDirection: 'column' }}>
      <FilterDropdown
        items={Object.keys(options.choices || {}).map(name => ({ value: name, label: name }))}
        value={selectedFromName}
        onChange={handleFromNameChange}
        placeholder="Select control (optional)"
        allowClear
      />
      <FilterDropdown
        items={choiceOptions}
        value={value?.choice || ''}
        onChange={handleChoiceChange}
        placeholder="Select choice value"
        searchable
      />
    </div>
  );
});

// Component for filtering by annotation text content
const AnnotationTextInput = observer(({ value, onChange, projectId }) => {
  const { options } = useAnnotationOptions(projectId);
  const [selectedFromName, setSelectedFromName] = useState(value?.from_name || '');

  const handleTextChange = (textValue) => {
    onChange({
      text: textValue,
      from_name: selectedFromName
    });
  };

  const handleFromNameChange = (fromName) => {
    setSelectedFromName(fromName);
    onChange({
      text: value?.text || '',
      from_name: fromName
    });
  };

  return (
    <div style={{ display: 'flex', gap: '8px', flexDirection: 'column' }}>
      <FilterDropdown
        items={options.from_names?.map(name => ({ value: name, label: name })) || []}
        value={selectedFromName}
        onChange={handleFromNameChange}
        placeholder="Select control (optional)"
        allowClear
      />
      <FilterInput
        type="text"
        value={value?.text || ''}
        onChange={handleTextChange}
        placeholder="Enter text to search"
      />
    </div>
  );
});

// Component for filtering by annotation type
const AnnotationTypeInput = observer(({ value, onChange, projectId }) => {
  const { options, loading } = useAnnotationOptions(projectId);

  if (loading) {
    return <FilterInput type="text" value={value} onChange={onChange} placeholder="Loading..." disabled />;
  }

  return (
    <FilterDropdown
      items={options.annotation_types?.map(type => ({ value: type, label: type })) || []}
      value={value}
      onChange={onChange}
      placeholder="Select annotation type"
    />
  );
});

// Component for filtering by numeric values in annotations
const AnnotationNumericInput = observer(({ value, onChange, projectId }) => {
  const { options } = useAnnotationOptions(projectId);
  const [selectedFromName, setSelectedFromName] = useState(value?.from_name || '');

  const handleValueChange = (numericValue) => {
    onChange({
      value: parseFloat(numericValue) || 0,
      from_name: selectedFromName
    });
  };

  const handleFromNameChange = (fromName) => {
    setSelectedFromName(fromName);
    onChange({
      value: value?.value || 0,
      from_name: fromName
    });
  };

  return (
    <div style={{ display: 'flex', gap: '8px', flexDirection: 'column' }}>
      <FilterDropdown
        items={options.from_names?.map(name => ({ value: name, label: name })) || []}
        value={selectedFromName}
        onChange={handleFromNameChange}
        placeholder="Select control (optional)"
        allowClear
      />
      <FilterInput
        type="number"
        value={value?.value || ''}
        onChange={handleValueChange}
        placeholder="Enter numeric value"
      />
    </div>
  );
});

// Filter definitions for annotation content
export const AnnotationLabelFilter = [
  {
    key: "contains",
    label: "contains label",
    valueType: "single",
    input: (props) => <AnnotationLabelInput {...props} />,
  },
  {
    key: "not_contains",
    label: "does not contain label",
    valueType: "single",
    input: (props) => <AnnotationLabelInput {...props} />,
  },
];

export const AnnotationChoiceFilter = [
  {
    key: "contains",
    label: "contains choice",
    valueType: "single",
    input: (props) => <AnnotationChoiceInput {...props} />,
  },
  {
    key: "not_contains",
    label: "does not contain choice",
    valueType: "single",
    input: (props) => <AnnotationChoiceInput {...props} />,
  },
];

export const AnnotationTextFilter = [
  {
    key: "contains",
    label: "text contains",
    valueType: "single",
    input: (props) => <AnnotationTextInput {...props} />,
  },
  {
    key: "not_contains",
    label: "text does not contain",
    valueType: "single",
    input: (props) => <AnnotationTextInput {...props} />,
  },
  {
    key: "equal",
    label: "text equals",
    valueType: "single",
    input: (props) => <AnnotationTextInput {...props} />,
  },
];

export const AnnotationTypeFilter = [
  {
    key: "equal",
    label: "has annotation type",
    valueType: "single",
    input: (props) => <AnnotationTypeInput {...props} />,
  },
  {
    key: "not_equal",
    label: "does not have annotation type",
    valueType: "single",
    input: (props) => <AnnotationTypeInput {...props} />,
  },
];

export const AnnotationNumericFilter = [
  {
    key: "equal",
    label: "equals",
    valueType: "single",
    input: (props) => <AnnotationNumericInput {...props} />,
  },
  {
    key: "greater",
    label: "greater than",
    valueType: "single",
    input: (props) => <AnnotationNumericInput {...props} />,
  },
  {
    key: "less",
    label: "less than",
    valueType: "single",
    input: (props) => <AnnotationNumericInput {...props} />,
  },
  {
    key: "greater_or_equal",
    label: "greater than or equal",
    valueType: "single",
    input: (props) => <AnnotationNumericInput {...props} />,
  },
  {
    key: "less_or_equal",
    label: "less than or equal",
    valueType: "single",
    input: (props) => <AnnotationNumericInput {...props} />,
  },
];