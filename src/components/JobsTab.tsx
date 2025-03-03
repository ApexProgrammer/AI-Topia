import React from 'react';
import { Box, List, ListItem, Typography, Paper, Chip, Divider } from '@mui/material';

interface Colonist {
    role: string;
    age: number;
    job?: {
        type: string;
        building?: {
            name: string;
            building_type: string;
        }
    };
    skills: {
        farming: number;
        mining: number;
        woodcutting: number;
        crafting: number;
    };
}

const JobsTab: React.FC = () => {
    // This would need to be connected to your game state
    const colonists: Colonist[] = window.game?.world?.colonists || [];

    // Group colonists by job type
    const jobGroups = {
        farmer: colonists.filter(c => c.role === 'farmer'),
        woodcutter: colonists.filter(c => c.role === 'woodcutter'),
        miner: colonists.filter(c => c.role === 'miner'),
        unemployed: colonists.filter(c => c.role === 'unemployed')
    };

    return (
        <Paper elevation={0}>
            {Object.entries(jobGroups).map(([jobType, workers]) => (
                <Box key={jobType} mb={2}>
                    <Typography variant="h6" sx={{ textTransform: 'capitalize' }}>
                        {jobType} ({workers.length})
                    </Typography>
                    <List>
                        {workers.map((colonist, index) => (
                            <ListItem 
                                key={index}
                                divider={index !== workers.length - 1}
                                sx={{ py: 1 }}
                            >
                                <Box width="100%">
                                    <Box display="flex" justifyContent="space-between" alignItems="center">
                                        <Typography>
                                            Age: {Math.floor(colonist.age)}
                                        </Typography>
                                        <Chip 
                                            label={colonist.job ? `Working at ${colonist.job.building?.name || 'Unknown'}` : 'Unemployed'}
                                            color={colonist.job ? "success" : "error"}
                                            size="small"
                                            variant="outlined"
                                        />
                                    </Box>
                                    <Box mt={1}>
                                        <Typography variant="body2" color="textSecondary">
                                            Skills: 
                                            {colonist.skills && Object.entries(colonist.skills).map(([skill, level]) => (
                                                <Chip
                                                    key={skill}
                                                    label={`${skill}: ${Math.floor(level)}`}
                                                    size="small"
                                                    sx={{ ml: 1 }}
                                                />
                                            ))}
                                        </Typography>
                                    </Box>
                                </Box>
                            </ListItem>
                        ))}
                    </List>
                    <Divider sx={{ my: 2 }} />
                </Box>
            ))}
            {colonists.length === 0 && (
                <Box p={2}>
                    <Typography>No colonists available.</Typography>
                </Box>
            )}
        </Paper>
    );
};

export default JobsTab;
