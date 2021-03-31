import React from 'react';
import Util from './helpers/util';

import Container from 'react-bootstrap/Container';
import Button from "react-bootstrap/Button";

export default class NftCard extends React.Component {
    constructor(props) {
        super(props);
    }

    render() {
        const { nft } = this.props;

        return (
            <div className="header-container">
                {nft.name}
            </div>
        );
    }
}
