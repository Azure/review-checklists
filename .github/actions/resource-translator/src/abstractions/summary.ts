export class Summary {
    newFileCount: number = 0;
    newFileTranslations: number = 0;

    updatedFileCount: number = 0;
    updatedFileTranslations: number = 0;

    constructor(
        public sourceLocale: string,
        public toLocales: string[]) {
    }

    get totalFileCount(): number {
        return this.newFileCount + this.updatedFileCount;
    }

    get totalTranslations(): number {
        return this.newFileTranslations + this.updatedFileTranslations;
    }

    get hasNewTranslations(): boolean {
        return this.totalTranslations > 0;
    }
}