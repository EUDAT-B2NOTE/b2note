export function debounce(action: (...args: any[]) => void, waitFor: number): (...args: any[]) => void {
    let timeout: number | undefined;

    return function (this: any) {
        let context = this;
        let args = arguments;

        let delayed = (): void => {
            action.apply(context, args);
            timeout = undefined;
        };

        if (timeout != undefined) {
            window.clearTimeout(timeout);
        }

        timeout = window.setTimeout(delayed, waitFor);
    };
}
