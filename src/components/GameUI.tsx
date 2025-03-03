import JobButton from './JobButton';
import React, { useState } from 'react';
import BuildingButton from './BuildingButton';
import JobsTab from './JobsTab';

export default function GameUI() {
    const [showBuildMenu, setShowBuildMenu] = useState(false);
    const [showJobMenu, setShowJobMenu] = useState(false);

    const handleBuildClick = () => {
        setShowBuildMenu(!showBuildMenu);
        setShowJobMenu(false); // Close job menu if open
    };

    const handleJobClick = () => {
        setShowJobMenu(!showJobMenu);
        setShowBuildMenu(false); // Close build menu if open
    };

    return (
        <div>
            <BuildingButton onClick={handleBuildClick} />
            <JobButton onClick={handleJobClick} />
            {showBuildMenu && (
                <div>
                    {/* Build menu content */}
                </div>
            )}
            {showJobMenu && (
                <JobsTab />
            )}
            {/* ...rest of the UI... */}
        </div>
    );
}
