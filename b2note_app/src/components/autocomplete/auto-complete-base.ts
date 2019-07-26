import { observable } from "aurelia-framework";
import { Indexer } from "./indexer";
import { AutoCompleteItem } from "./auto-complete-item";
import { SuggestionsLogic } from "./suggestions-logic";
import { SuggestionsElementLogic } from "./suggestions-element-logic";
import { debounce } from "./debounce";

export abstract class AutoCompleteBase<T extends Indexer> {
    // public API:
    public suggestionsProvider: (value: string) => Promise<T[]>;
    public suggestionsDebounce: number;
    public minSearchValueLength: number;
    public placeholder: string;
    public isDisabledProperty: string;
    public disableSelected: boolean;
    public itemByValueProvider: (value: string) => T;
    public additionalClassInput: string;

    public get isCurrentValueInvalid(): boolean {
        return this.getInitialDisplayValue() !== this._value && this._suggestionsElementLogic.inputElement !== document.activeElement;
    }

    // view-related properties
    @observable({ changeHandler: "valueChanged" }) private _value: string;
    private _suggestionsLogic: SuggestionsLogic<T>;
    private _suggestionsElementLogic: SuggestionsElementLogic;

    // real privates
    private _comittedValue: string;
    private _bindingContext: Object;
    private _debouncedRefreshSuggestions: (searchValue: string) => void;

    protected constructor() {
        this._suggestionsLogic = new SuggestionsLogic<T>();
        this._suggestionsElementLogic = new SuggestionsElementLogic();
    };

    public bind(bindingContext: Object): void {
        this._bindingContext = bindingContext;
        this.initializeSuggestionsElementLogic();
        this.initializeSuggestionsLogic();
        this.initializeDebouncedRefresh();
        this.updateValueWithoutChangeTrigger();
    }

    protected abstract getInitialDisplayValue(): string;
    protected abstract selectItem(item: T | undefined): void;
    protected abstract isSelected(item: T): boolean;

    protected reset(): void {
        this.resetSuggestions();
        this.updateValueWithoutChangeTrigger();
    }

    private resetSuggestions(): void {
        this._suggestionsElementLogic.hideSuggestions();
        this._suggestionsLogic.clearSuggestions();
    }

    private suggestionsProviderChanged(): void {
        this.initializeSuggestionsElementLogic();
        this.initializeSuggestionsLogic();
    }

    private suggestionsDebounceChanged(): void {
        this.initializeDebouncedRefresh();
    }

    private minSearchValueLengthChanged(): void {
        this._suggestionsLogic.minSearchValueLength = this.minSearchValueLength;
    }

    private async valueChanged(newValue: string, oldValue: string): Promise<void> {
        if (this._comittedValue === newValue) {
            return;
        }

        this._comittedValue = newValue;
        this.resetSuggestions();

        // manual debounce
        // note: do not use Aurelia's binding debounce feature, because we need the value immediately here in our view model for things like the itemByValueProvider.
        this._debouncedRefreshSuggestions(newValue);
    }

    private keyPressed(keyboardEvent: KeyboardEvent): boolean {
        let keyCode = keyboardEvent.keyCode;
        let areSuggestionsHidden = this._suggestionsElementLogic.areSuggestionsHidden;

        // special case => re-open suggestions
        if (keyboardEvent.altKey && keyCode === 13) {
            this.refreshSuggestionsAsync(this._value); // ignore returned promise
            return false;
        }

        if (keyboardEvent.altKey || keyboardEvent.ctrlKey || keyboardEvent.shiftKey) {
            // do not trigger any features if modifier keys are pressed
            return true;
        }

        switch (keyCode) {
            case 27:
                if (!areSuggestionsHidden) {
                    this.resetSuggestions();
                }
                else {
                    // now escape resets the entered text
                    this.updateValueWithoutChangeTrigger();
                }

                break;
            case 9:
                if (this._suggestionsLogic.currentHighlightedIndex > -1) {
                    this.select(this._suggestionsLogic.currentHighlightedIndex);
                }

                break;
            case 13:
                if (this._value == undefined || this._value.trim() === "") {
                    this.selectItem(undefined);
                    break;
                }

                if (this._suggestionsLogic.currentHighlightedIndex > -1) {
                    this.select(this._suggestionsLogic.currentHighlightedIndex);
                }
                else if (this.itemByValueProvider != undefined) {
                    let newItem = this.itemByValueProvider.call(this._bindingContext, this._value);
                    this.selectItemAndReset(newItem);
                }

                break;
            default:
                break;
        }

        if (!areSuggestionsHidden) {
            return this._suggestionsLogic.applyHighlightingKeyboardFeatures(keyboardEvent);
        }

        return true;
    }

    private mousemove(event: MouseEvent, index: number): boolean {
        if (event.movementX === 0 && event.movementY === 0) {
            // some browsers report mouse move event when the content under the cursor moves => i.e. if we programmatically scroll the list => prevent highlighting then!
            return false;
        }

        this._suggestionsLogic.highlight(index);
        return true;
    }

    private select(itemIndex: number): void {
        let item = this._suggestionsLogic.getSuggestion(itemIndex);
        if (item != undefined) {
            this.selectItemAndReset(item);
        }
    }

    private selectItemAndReset(item: T): void {
        this.selectItem(item);
        this.resetSuggestions();
        this.updateValueWithoutChangeTrigger();
    }

    private async refreshSuggestionsAsync(value: string): Promise<void> {
        try {
            // optimization: this may be called debounced, so the given value potentially is not valid anymore => no need to call into the refresh at all
            if (value !== this._value) {
                return;
            }

            this.resetSuggestions();
            let successful = await this._suggestionsLogic.refreshSuggestionsAsync(value, (x: string) => x === this._value && this._suggestionsElementLogic.inputElement === document.activeElement);
            if (successful) {
                this._suggestionsElementLogic.showSuggestions();
            }
        }
        catch (error) {
            this.resetSuggestions();
        }
    }

    private initializeDebouncedRefresh(): void {
        this._debouncedRefreshSuggestions = debounce(this.refreshSuggestionsAsync, this.suggestionsDebounce);
    }

    private initializeSuggestionsElementLogic(): void {
        this._suggestionsElementLogic.hideSuggestions();
    }

    private initializeSuggestionsLogic(): void {
        let actualSuggestionProvider: (searchValue: string) => Promise<T[]> = (searchValue: string) => this.suggestionsProvider.call(this._bindingContext, searchValue);
        this._suggestionsLogic.suggestionsProvider = actualSuggestionProvider;
        this._suggestionsLogic.isSelectedValidator = (item: T): boolean => this.isSelected(item);
        this._suggestionsLogic.isDisabledValidator = (item: T): boolean => {
            if (this.disableSelected && this.isSelected(item)) {
                return true;
            }

            return this.isDisabledProperty != undefined && typeof (item[this.isDisabledProperty]) === "boolean" && <boolean>item[this.isDisabledProperty];
        };
        this._suggestionsLogic.minSearchValueLength = this.minSearchValueLength;
        this._suggestionsLogic.clearSuggestions();
    }

    private updateValueWithoutChangeTrigger(): void {
        // the purpose of this method is to set the "backing field" of the value property before the actual value property.
        // the backing field value is checked in the valueChanged event handler, which skips its logic if the stored _value
        // already is equal to the new value
        this._comittedValue = this.getInitialDisplayValue();
        this._value = this._comittedValue;
    }

  /**
   * Sets suggestions immediatelly, .e.g. from previous get or cache when suggestions was obtained from different source.
   * @param suggestions
   */
  public setSuggestions(suggestions:T[]){
      this.reset();
      this._suggestionsLogic.setSuggestions(suggestions);
      this._suggestionsElementLogic.showSuggestions();
    }

    protected _getRawValue(){
    return this._value;
    }

}
