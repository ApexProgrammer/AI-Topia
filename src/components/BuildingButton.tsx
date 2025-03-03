import React from 'react';
import { Button } from '@mui/material';
import HomeWorkIcon from '@mui/icons-material/HomeWork';

interface BuildingButtonProps {
    onClick: () => void;
}

const BuildingButton: React.FC<BuildingButtonProps> = ({ onClick }) => {
    return (
        <Button
            variant="contained"
            startIcon={<HomeWorkIcon />}
            onClick={onClick}
            sx={{
                position: 'absolute',
                left: 10,
                top: 10,
                backgroundColor: '#4a4a4a',
                '&:hover': {
                    backgroundColor: '#666666',
                },
            }}
        >
            Build
        </Button>
    );
};

export default BuildingButton;
