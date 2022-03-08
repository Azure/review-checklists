import { PortableObjectToken } from "../src/file-formats/po-file";

test("PO-TOKEN: parses invalid values correctly", async () => {
    let token = new PortableObjectToken(undefined);
    expect(token.isInsignificant).toBeTruthy();

    token = new PortableObjectToken(null);
    expect(token.isInsignificant).toBeTruthy();

    token = new PortableObjectToken('');
    expect(token.isInsignificant).toBeTruthy();

    token = new PortableObjectToken('     ');
    expect(token.isInsignificant).toBeTruthy();
});

test("PO-TOKEN: parses line correctly", async () => {
    let token = new PortableObjectToken('msgid "There is one item."');
    expect(token.isInsignificant).toBeFalsy();
    expect(token.id).toEqual('msgid');
    expect(token.value).toEqual('"There is one item."');

    token = new PortableObjectToken('msgid_plural "There are {0} items."');
    expect(token.isInsignificant).toBeFalsy();
    expect(token.id).toEqual('msgid_plural');
    expect(token.value).toEqual('"There are {0} items."');
});