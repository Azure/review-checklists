export interface XliffFile {
    xliff: Xliff;
}

export interface LanguageAttributes {
    srcLang: string;
    trgLang: string;
}

export interface Xliff {
    $: LanguageAttributes;
    file: File[];
}

export interface File {
    $: IdAttribute;
    unit: Unit[];
}

export interface IdAttribute {
    id: number;
}

export interface Unit {
    segment: Segment[];
}

export interface Segment {
    source: string[];
    target: string[];
}

export const XliffFileKeyDelimiter = '::';

export const traverseXliff =
    (instance: XliffFile, fileIndex: number, sourceName: string, segmentAction: (segment: Segment) => void) => {
        if (instance && segmentAction) {
            if (instance.xliff.file && instance.xliff.file.length > fileIndex) {
                const unit =
                    instance.xliff.file[fileIndex].unit.find(
                        unit => unit.segment.find(s => s.source.includes(sourceName)));
                if (unit) {
                    segmentAction(
                        unit.segment.find(s => s.source.includes(sourceName))!);
                }
            }
        }
    }

export const findInXliff =
    (instance: XliffFile, fileIndex: number, sourceName: string): Segment | undefined => {
        if (instance) {
            if (instance.xliff.file && instance.xliff.file.length > fileIndex) {
                const unit =
                    instance.xliff.file[fileIndex].unit.find(
                        unit => unit.segment.find(s => s.source.includes(sourceName)));
                if (unit) {
                    return unit.segment.find(s => s.source.includes(sourceName))!;
                }
            }
        }
    }