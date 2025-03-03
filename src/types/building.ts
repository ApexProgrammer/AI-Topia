export interface Building {
    id: string;
    name: string;
    description: string;
    cost: {
        wood?: number;
        stone?: number;
        food?: number;
    };
    position: {
        x: number;
        y: number;
    };
}

export interface World {
    buildings: Building[];
    // ...other world properties...
}
