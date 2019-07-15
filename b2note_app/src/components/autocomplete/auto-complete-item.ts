export class AutoCompleteItem<T> {
    public readonly value: T;
    public readonly index: number;
    public isSelected: boolean;
    public isDisabled: boolean;
    public isHighlighted: boolean;

    public constructor(value: T, index: number, isSelected: boolean, isDisabled: boolean) {
        this.value = value;
        this.index = index;
        this.isSelected = isSelected;
        this.isDisabled = isDisabled;
        this.isHighlighted = false;
    }
}
