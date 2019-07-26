import { bindable, bindingMode } from "aurelia-framework";
import { Indexer } from "./indexer";
import { AutoCompleteBase } from "./auto-complete-base";

export class GoodAutoCompleteCustomElement<T extends Indexer> extends AutoCompleteBase<T> {
    // inheritance is not supported for binding metadata of components => we need to duplicate the base class properties and decorate them here
    @bindable public suggestionsProvider: (value: string) => Promise<T[]>;
    @bindable public suggestionsDebounce: number = 500;
    @bindable public minSearchValueLength: number = 2;
    @bindable public placeholder: string;
    @bindable public isDisabledProperty: string;
    @bindable public disableSelected: boolean;
    @bindable public itemByValueProvider: (value: string) => T;   
    @bindable public additionalClassInput: string;

    // public API:
    @bindable({ defaultBindingMode: bindingMode.twoWay }) public selectedItem: T | undefined;

    protected getInitialDisplayValue(): string {
        return this.selectedItem != undefined ? this.selectedItem.toString() : "";
    }

    protected selectItem(item: T | undefined): void {
        this.selectedItem = item;
    }

    protected isSelected(item: T): boolean {
        return this.selectedItem === item;
    }

    private selectedItemChanged(): void {
        this.reset();
    }

    public getRawValue(){
      return this._getRawValue()
    }

}
