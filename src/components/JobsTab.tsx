import React from 'react';
import { Box, List, ListItem, Typography, Paper, Chip } from '@mui/material';

interface JobStats {
    title: string;
    current: number;
    maximum: number;
}

interface JobsTabProps {
    jobStats: JobStats[];
}

const JobsTab: React.FC<JobsTabProps> = ({ jobStats }) => {
    if (!Array.isArray(jobStats)) {
        console.error('Invalid jobStats provided:', jobStats);
        return <Typography color="error">Error loading jobs data</Typography>;
    }

    if (jobStats.length === 0) {
        return (
            <Box p={2}>
                <Typography>No jobs available yet. Build some buildings to create job positions.</Typography>
            </Box>
        );
    }

    return (
        <Paper elevation={0}>
            <List>
                {jobStats.map((job, index) => (
                    <ListItem 
                        key={`${job.title}-${index}`} 
                        divider={index !== jobStats.length - 1}
                        sx={{ py: 1 }}
                    >
                        <Box display="flex" width="100%" justifyContent="space-between" alignItems="center">
                            <Typography>{job.title}</Typography>
                            <Chip
                                label={`${job.current}/${job.maximum}`}
                                color={job.current === job.maximum ? "success" : 
                                       job.current === 0 ? "error" : "warning"}
                                size="small"
                                variant="outlined"
                            />
                        </Box>
                    </ListItem>
                ))}
            </List>
        </Paper>
    );
};

export default JobsTab;
