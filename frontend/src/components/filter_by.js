import React from 'react';

export default class FilterBy extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            for_sale: true,
            claimed: true,
            empty: true,
        };
    }

    componentDidUpdate() {
        this.props.onChange( this.state )
    }

    render() {
        const { for_sale, claimed, empty } = this.state;

        return (
            <div class="map-grid-filter">
                <ul>
                    <li>
                        <label className="check_item check_item_1" onChange={() => this.setState({ for_sale: !for_sale })}>For sale
                            <input type="checkbox" checked={for_sale} tabIndex="0"/>
                            <span className="checkmark"></span>
                        </label>
                    </li>
                    <li>
                        <label className="check_item check_item_2" onChange={() => this.setState({ claimed: !claimed })}>Claimed
                            <input type="checkbox" checked={claimed} tabIndex="2"/>
                            <span className="checkmark"></span>
                        </label>
                    </li>
                    <li>
                        <label className="check_item check_item_3" onChange={() => this.setState({ empty: !empty})}>Empty
                            <input type="checkbox" checked={empty} tabIndex="3"/>
                            <span className="checkmark"></span>
                        </label>
                    </li>
                    <li>
                        <label className="check_item check_item_4">A thing
                            <input type="checkbox" tabIndex="4"/>
                            <span className="checkmark"></span>
                        </label>
                    </li>
                </ul>
            </div>
        );
    }
}
