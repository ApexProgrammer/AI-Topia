export interface Job {
    employee: string | null;
    type: string;
    building_id: string;
}

export interface Building {
    id: string;
    building_type: string;
    jobs: Job[];
    position: {
        x: number;
        y: number;
    };
}

export interface World {
    buildings: Building[];
    // ...other world properties...
}
