const ethUtil = require('ethereumjs-util');

if ( process.argv.length != 5 ) {
    console.log(`node ${process.argv[1]} public nonce sig`);
    process.exit(-1);
    return;
}

const publicAddress = process.argv[2];
const nonce = process.argv[3];
const signature = process.argv[4];

try {
    const msgBuffer = ethUtil.toBuffer(nonce);
    const msgHash = ethUtil.hashPersonalMessage(msgBuffer);
    const signatureBuffer = ethUtil.toBuffer(signature);
    const signatureParams = ethUtil.fromRpcSig(signatureBuffer);
    const publicKey = ethUtil.ecrecover(
      msgHash,
      signatureParams.v,
      signatureParams.r,
      signatureParams.s
    );
    const addressBuffer = ethUtil.publicToAddress(publicKey);
    const address = ethUtil.bufferToHex(addressBuffer);

    // The signature verification is successful if the address found with
    // ecrecover matches the initial publicAddress
    console.log( address.toLowerCase())
    console.log( publicAddress.toLowerCase() )
    process.exit( (address.toLowerCase() === publicAddress.toLowerCase())? 0: 1 );
}
catch (err) {
    console.log( err );
    process.exit(2);
}
