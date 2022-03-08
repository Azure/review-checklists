export interface ResourceFile {
    root: Root;
}

export interface Root {
    data: Data[];
}

export interface Data {
    $: NameAttribute;
    value: string[];
}

export interface NameAttribute {
    name: string;
}

export const traverseResx =
    (instance: ResourceFile, name: string, dataAction: (data: Data) => void) => {
        if (instance && instance.root && instance.root.data) {
            const data =
                instance.root.data.find(d => d.$.name === name);
            if (data) {
                dataAction(data);
            }
        }
};