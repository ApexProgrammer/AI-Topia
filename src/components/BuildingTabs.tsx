import React, { useState } from 'react';
import { Tabs, Tab, Box } from '@mui/material';

interface BuildingTabsProps {
    children: React.ReactNode;
}

const BuildingTabs: React.FC<BuildingTabsProps> = ({ children }) => {
    const [value, setValue] = useState(0);

    const handleChange = (event: React.SyntheticEvent, newValue: number) => {
        setValue(newValue);
    };

    return (
        <Box sx={{ width: '100%' }}>
            <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
                <Tabs value={value} onChange={handleChange}>
                    <Tab label="Buildings" />
                </Tabs>
            </Box>
            <Box sx={{ p: 2 }}>
                {value === 0 && (
                    <div>{children}</div>
                )}
            </Box>
        </Box>
    );
};

export default BuildingTabs;
