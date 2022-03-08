import { OriginalFileMap } from "./original-file-map";

export type RestextFile = OriginalFileMap & {
    [key: string]: string;
}