import { AutoCompleteItem } from "./auto-complete-item";

export class SuggestionsLogic<T> {

    public isSelectedValidator: (item: T) => boolean;
    public isDisabledValidator: (item: T) => boolean;
    public minSearchValueLength: number = 2;
    public currentHighlightedIndex: number = -1;
    public suggestionsProvider: (value: string) => Promise<T[]>;

    public get currentSuggestions(): Array<AutoCompleteItem<T>> {
        return this._suggestions;
    }

    private _suggestions: Array<AutoCompleteItem<T>> = [];

    public highlight(itemIndex: number): void {
        if (this._suggestions == undefined || this._suggestions.length === 0) {
            this.currentHighlightedIndex = -1;
            return;
        }

        let newHighlightedIndex = Math.max(0, Math.min(this._suggestions.length - 1, itemIndex));
        if (this.currentHighlightedIndex === newHighlightedIndex) {
            return;
        }

        if (this._suggestions[newHighlightedIndex].isDisabled) {
            return;
        }

        if (this.currentHighlightedIndex > -1 && this.currentHighlightedIndex < this._suggestions.length) {
            this._suggestions[this.currentHighlightedIndex].isHighlighted = false;
        }

        this.currentHighlightedIndex = newHighlightedIndex;
        this._suggestions[newHighlightedIndex].isHighlighted = true;
    }

    public clearSuggestions(): void {
        this.currentHighlightedIndex = -1;
        if (this._suggestions != undefined) {
            this._suggestions.splice(0);
        }
    }

    public async refreshSuggestionsAsync(searchValue: string, isSearchValueStillValid: (searchValue: string) => boolean): Promise<boolean> {
        if (searchValue == undefined || searchValue.length < this.minSearchValueLength) {
            return false;
        }

        let suggestions = await this.getSuggestionsAsync(searchValue);
        if (!isSearchValueStillValid(searchValue)) {
            // while waiting for the suggestions result asynchronously, the value has changed or the user has tabbed away etc.
            // => this suggestions result is not valid anymore, do not proceed
            return false;
        }

        if (suggestions == undefined || suggestions.length === 0) {
            return false;
        }

        this._suggestions.splice(0);
        let autoCompleteItems = suggestions.map<AutoCompleteItem<T>>((value, index) => new AutoCompleteItem<T>(value, index, this.isSelectedValidator(value), this.isDisabledValidator(value)));
        this._suggestions.push.apply(this._suggestions, autoCompleteItems);

        this.highlight(this.getNextPossibleIndexToHighlight(-1, 1));
        return true;
    }

    public async setSuggestions(suggestions: T[]){
        this._suggestions.splice(0);
        let autoCompleteItems = suggestions.map<AutoCompleteItem<T>>((value, index) => new AutoCompleteItem<T>(value, index, this.isSelectedValidator(value), this.isDisabledValidator(value)));
        this._suggestions.push.apply(this._suggestions, autoCompleteItems);
        this.highlight(this.getNextPossibleIndexToHighlight(-1, 1));
        return true;
    }

    public applyHighlightingKeyboardFeatures(keyboardEvent: KeyboardEvent): boolean {
        if (keyboardEvent.altKey || keyboardEvent.shiftKey || keyboardEvent.ctrlKey) {
            // we do not want to interfere with e.g. selection of text (shift + arrows) even when the suggestions are visible
            return true;
        }

        let keyCode = keyboardEvent.keyCode;

        switch (keyCode) {
            case 40: // down
                this.highlight(this.getNextPossibleIndexToHighlight(this.currentHighlightedIndex, 1));
                break;
            case 38: // up
                this.highlight(this.getNextPossibleIndexToHighlight(this.currentHighlightedIndex, -1));
                break;
            case 34: // page down
                let higherOffset = 10;
                let nextHigherIndex = this.getNextPossibleIndexToHighlight(this.currentHighlightedIndex, higherOffset);
                while (nextHigherIndex === this.currentHighlightedIndex && higherOffset > 1) {
                    higherOffset--;
                    nextHigherIndex = this.getNextPossibleIndexToHighlight(this.currentHighlightedIndex, higherOffset);
                }

                this.highlight(nextHigherIndex);
                break;
            case 33: // page up
                let lowerOffset = -10;
                let nextLowerIndex = this.getNextPossibleIndexToHighlight(this.currentHighlightedIndex, lowerOffset);
                while (nextLowerIndex === this.currentHighlightedIndex && lowerOffset < -1) {
                    lowerOffset++;
                    nextLowerIndex = this.getNextPossibleIndexToHighlight(this.currentHighlightedIndex, lowerOffset);
                }

                this.highlight(nextLowerIndex);
                break;
            case 35: // end
                this.highlight(this.getNextPossibleIndexToHighlight(this._suggestions.length, -1));
                break;
            case 36: // home
                this.highlight(this.getNextPossibleIndexToHighlight(-1, 1));
                break;
            default:
                return true;
        }

        return false;
    }

    public getSuggestion(itemIndex: number): T | undefined {
        if (this._suggestions == undefined || itemIndex < 0 || itemIndex > this._suggestions.length - 1) {
            return undefined;
        }

        return this._suggestions[itemIndex].value;
    }

    private getNextPossibleIndexToHighlight(startIndex: number, desiredOffset: number): number {
        if (this._suggestions == undefined) {
            return -1;
        }

        if (desiredOffset === 0) {
            return !this._suggestions[startIndex].isDisabled ? startIndex : this.currentHighlightedIndex;
        }

        let potentialNextIndex = startIndex + desiredOffset;
        while (potentialNextIndex > -1 && potentialNextIndex < this._suggestions.length && this._suggestions[potentialNextIndex].isDisabled) {
            if (desiredOffset > 0) {
                potentialNextIndex++;
            }
            else {
                potentialNextIndex--;
            }
        }

        return potentialNextIndex < 0 || potentialNextIndex > this._suggestions.length - 1 ? this.currentHighlightedIndex : potentialNextIndex;
    }

    private async getSuggestionsAsync(searchValue: string): Promise<T[]> {
        let suggestions = <T[]>(await this.suggestionsProvider(searchValue));
        if (suggestions == undefined || suggestions.length === 0) {
            return [];
        }

        return suggestions;
    }
}
