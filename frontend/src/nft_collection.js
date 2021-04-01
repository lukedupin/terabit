import React from 'react';
import Util from './helpers/util';
import NftCard from './nft_card';

export default class NftCollection extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
        };

        this.handleBuy = this.handleBuy.bind(this);
    }

    handleBuy() {
    }

    render() {
        const { human, nfts } = this.props;

        return (
            <div className="row">
                <div className="map-listing">
                    <div className="map-listing-head">
                        <img className="map-listing-profile" src={human.profile_image} alt="img"/>
                        <div className="map-listing-profile-deets">
                            <a className="user-name" href="#">{human.username}</a>
                            <p className="user-byline">$0.00</p>
                        </div>
                        <div className="map-listing-cta">
                            <a className="btn" href="#" onClick={this.handleBuy}>Buy</a>
                        </div>
                    </div>
                    <div className="map-listing-item">
                        <img className="map-listing-image" src="/static/images/image-location-default.jpg" alt="img"/>
                        <p className="location-latlong">43.615021, -116.202316</p>
                        <p className="location-story">Lorem ipsum dolor sit amet, consectetur adipiscing elit. Vestibulum libero sapien, mattis sed cursus non, sollicitudin vitae leo. Nullam auctor et dui sit amet ultricies. Nullam eget porttitor nisi, vel condimentum erat.</p>
                        <p className="tokens-header">Tokens</p>
                        <p className="token-title">Benny Wonderbear</p>
                        <p className="token-desc">#1821767 Gen 8</p>
                        <p className="token-title">Benny Wonderbear</p>
                        <p className="token-desc">#1821767 Gen 8</p>
                        <p className="token-title">Benny Wonderbear</p>
                        <p className="token-desc">#1821767 Gen 8</p>
                    </div>
                </div>
            </div>
        );
    }
}
