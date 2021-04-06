import React from 'react';

import NftCard from './nft_card';
import Util from '../helpers/util';

export default class NftCollection extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
        };
    }

    render() {
        const { human } = this.props;

        return (
            <div className="row">
                <div className="map-listing">
                    <div className="map-listing-head">
                        <img className="map-listing-profile" src={human.profile_image} alt="img"/>
                        <div className="map-listing-profile-deets">
                            <a className="user-name" href="#">{human.username}</a>
                            <p className="user-byline">long balls goes here</p> 
                        </div>
                    </div>

                    {Object.entries(human.nfts).map( ([key, nft]) =>
                        <NftCard key="{key}" nft={nft}/>)}
                </div>
            </div>
        );
    }
}
