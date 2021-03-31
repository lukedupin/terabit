import React from 'react';
import Util from './helpers/util';
import NftCard from './nft_card';

export default class NftCollection extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
        };
    }

    render() {
        const { human, nfts } = this.props;

        console.log(human.username);

        return (
            <div className="nft-collection">
                <img src={human.image_profile} />
                <div>{human.username}</div>
                {Object.entries(nfts).map(([k, nft]) => <NftCard nft={nft} />)}
            </div>
        );
    }
}
