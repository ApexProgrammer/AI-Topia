import React from 'react';
import { Button } from '@mui/material';
import WorkIcon from '@mui/icons-material/Work';

interface JobButtonProps {
    onClick: () => void;
}

const JobButton: React.FC<JobButtonProps> = ({ onClick }) => {
    return (
        <Button
            variant="contained"
            startIcon={<WorkIcon />}
            onClick={onClick}
            sx={{
                position: 'absolute',
                left: 100, // Position it next to the building button
                top: 10,
                backgroundColor: '#4a4a4a',
                '&:hover': {
                    backgroundColor: '#666666',
                },
            }}
        >
            Jobs
        </Button>
    );
};

export default JobButton;
