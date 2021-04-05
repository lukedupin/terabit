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
            <div className="map-grid-filter">
                <ul>
                    <li>
                        <label className="check_item check_item_4" onChange={() => this.setState({ for_sale: !for_sale })}>For sale
                            <input type="checkbox" checked={for_sale} tabIndex="0" readOnly={true}/>
                            <span className="checkmark"></span>
                        </label>
                    </li>
                    <li>
                        <label className="check_item check_item_2" onChange={() => this.setState({ claimed: !claimed })}>Claimed
                            <input type="checkbox" checked={claimed} tabIndex="2" readOnly={true} />
                            <span className="checkmark"></span>
                        </label>
                    </li>
                    <li>
                        <label className="check_item check_item_1" onChange={() => this.setState({ empty: !empty})}>Empty
                            <input type="checkbox" checked={empty} tabIndex="3" readOnly={true} />
                            <span className="checkmark"></span>
                        </label>
                    </li>
                </ul>
            </div>
        );
    }
}
