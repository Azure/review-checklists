import { Builder, Parser } from "xml2js";

export class XmlFileParser {
    static async fromXml<TFile>(xml: string): Promise<TFile> {
        const parser = new Parser();
        const xliffXml = await parser.parseStringPromise(xml);
        return xliffXml as TFile;
    }

    static toXml<T>(instance: T): string {
        const builder = new Builder();
        var xliffXml = builder.buildObject(instance);
        return xliffXml;
    }
}