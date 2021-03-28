import React from 'react';

class Checkbox extends  React.Component {
    constructor(props) {
        super(props);
        this.state = {
            checked: true,
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
        const { checked, label, tab_idx } = this.state;
        return (
            <div className="ui checkbox">
                <input
                    type="checkbox"
                    className="hidden"
                    readOnly=""
                    checked={checked}
                    onChange={this.handleToggle}
                    tabIndex={tab_idx}/>
                <label onClick={this.handleToggle}>{label}</label>
            </div>
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

    componentDidMount() {
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
            <div className="filter_by">
                <Checkbox onChange={this.handleChange} label="For sale" tab_idx="0" />
                <Checkbox onChange={this.handleChange} label="Claimed" tab_idx="1" />
                <Checkbox onChange={this.handleChange} label="Empty" tab_idx="2" />
            </div>
        );
    }
}
