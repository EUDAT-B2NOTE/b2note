import { bindable, bindingMode } from "aurelia-framework";
import { Indexer } from "./indexer";
import { AutoCompleteBase } from "./auto-complete-base";

export class GoodMultiAutoCompleteCustomElement<T extends Indexer> extends AutoCompleteBase<T> {
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
    @bindable({ defaultBindingMode: bindingMode.twoWay }) public selectedItems: T[] = [];

    protected getInitialDisplayValue(): string {
        return "";
    }

    protected selectItem(item: T | undefined): void {
        if (this.selectedItems == undefined) {
            this.selectedItems = [];
        }

        if (item != undefined) {
            this.selectedItems.push(item);
        }
    }

    protected remove(itemIndex: number): void {
        if (itemIndex < 0 || itemIndex > this.selectedItems.length - 1) {
            return;
        }

        this.selectedItems.splice(itemIndex, 1);

        // note: when the user clicks the remove-link of an item, no blur-event for the input is raised
        // => to prevent old entries from e.g. being wrongly displayed as selected, close the suggestions
        this.reset();
    }

    protected isSelected(item: T): boolean {
        return this.selectedItems.indexOf(item) > -1;
    }

    private selectedItemsChanged(): void {
        this.reset();
    }
}
