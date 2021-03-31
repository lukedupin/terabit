import React from 'react';

class Checkbox extends  React.Component {
    constructor(props) {
        super(props);
        this.state = {
            checked: true,
            klass: "",
            label: props.label,
            tab_idx: props.tab_idx,
        };

        this.handleToggle = this.handleToggle.bind(this);
    }

    handleToggle() {
        const checked = !this.state.checked
        this.setState({ checked });
        this.props.onChange( this.state.label, checked )
    }

    render() {
        const { checked, klass, label, tab_idx } = this.state;
        return (
            <label className={klass} onClick={this.handleToggle}>{label}
                <input type="checkbox" checked={checked} onChange={this.handleToggle} tabIndex={tab_idx}/>
                <span className="checkmark"></span>
            </label>
        );
    }
}

export default class FilterBy extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            for_sale: true,
            claimed: true,
            empty: true,
        };

        this.handleChange = this.handleChange.bind(this);
    }

    componentDidUpdate() {
        this.props.onChange( this.state )
    }

    handleChange( label, checked ) {
        switch (label) {
            case "For sale":
                this.setState({for_sale: checked})
                break;

            case "Claimed":
                this.setState({claimed: checked})
                break;

            case "Empty":
                this.setState({empty: checked})
                break;

            default: break
        }
    }

    render() {
        const { for_sale, claimed, empty } = this.state;

        return (
            <div class="map-grid-filter">
                <ul>
                    <li>
                        <Checkbox onChange={this.handleChange} klass="check_item check_item_1" label="For sale" tab_idx="0" />
                    </li>
                    <li>
                        <Checkbox onChange={this.handleChange} klass="check_item check_item_2" label="Claimed" tab_idx="1" />
                    </li>
                    <li>
                        <Checkbox onChange={this.handleChange} klass="check_item check_item_3" label="Empty" tab_idx="2" />
                    </li>
                    <li>
                        <Checkbox onChange={this.handleChange} klass="check_item check_item_4" label="A thing" tab_idx="3" />
                    </li>
                </ul>
            </div>
        );
    }
}
