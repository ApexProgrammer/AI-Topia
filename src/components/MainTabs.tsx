import { Tabs, Tab, Box } from '@mui/material';
import React, { useState } from 'react';
import BuildingsTab from './BuildingsTab';
import ColonistTab from './ColonistTab';
import JobsTab from './JobsTab';

interface TabPanelProps {
    children?: React.ReactNode;
    index: number;
    value: number;
}

function TabPanel(props: TabPanelProps) {
    const { children, value, index, ...other } = props;

    return (
        <div
            role="tabpanel"
            hidden={value !== index}
            id={`simple-tabpanel-${index}`}
            aria-labelledby={`simple-tab-${index}`}
            {...other}
        >
            {value === index && (
                <Box sx={{ p: 3 }}>
                    {children}
                </Box>
            )}
        </div>
    );
}

export default function MainTabs() {
    const [value, setValue] = useState(0);

    const handleChange = (event: React.SyntheticEvent, newValue: number) => {
        setValue(newValue);
    };

    return (
        <Box sx={{ width: '100%' }}>
            <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
                <Tabs value={value} onChange={handleChange}>
                    <Tab label="Buildings" />
                    <Tab label="Jobs" />
                    <Tab label="Colonists" />
                </Tabs>
            </Box>
            <TabPanel value={value} index={0}>
                <BuildingsTab />
            </TabPanel>
            <TabPanel value={value} index={1}>
                <JobsTab />
            </TabPanel>
            <TabPanel value={value} index={2}>
                <ColonistTab />
            </TabPanel>
        </Box>
    );
}
