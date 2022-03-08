export interface PortableObjectFile {
    tokens: PortableObjectToken[];
}

const firstWhitespace: RegExp = /\s+(.*)/;

// https://www.yogihosting.com/portable-object-aspnet-core/

export class PortableObjectToken {
    private _isInsignificant: boolean;
    private _identifier: string | null = null;
    private _value: string | null = null;

    get id(): string | null {
        return this._identifier;
    }

    get value(): string | null {
        return this._value;
    }

    set value(value: string | null) {
        this._value = value;
    }

    get isInsignificant(): boolean {
        return this._isInsignificant;
    }

    get isCommentLine(): boolean {
        return !!this.line && this.line.startsWith('#:');
    }

    constructor(public line: string | null | undefined) {
        if (line && line.trim()) {
            const keyValuePair = line.split(firstWhitespace);
            this._identifier = keyValuePair[0];
            this._value = keyValuePair.length > 1 ? keyValuePair[1] : null;
            this._isInsignificant = false;
        } else {
            this._isInsignificant = true;
        }
    }
}

export type PortableObjectTokenIdentifier =
    /**
     * Used to identify a translatable string, which is the source.
    */
    'msgid' |
    
    /**
     * Used to identify a translatable string alternative, in plural form as the source.
    */
    'msgid_plural' |
    
    /**
     * Used to identify the translated string value. Multiple can exist as an array, 
     * (for example, msgstr[0], msgstr[1], msgstr[2], etc.).
    */
    'msgstr';