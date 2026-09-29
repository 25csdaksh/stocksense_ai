declare namespace React {
  export type ReactNode =
    | ReactElement
    | string
    | number
    | Iterable<ReactNode>
    | ReactPortal
    | boolean
    | null
    | undefined;

  export interface ReactElement<P = any, T extends string | JSXElementConstructor<any> = string | JSXElementConstructor<any>> {
    type: T;
    props: P;
    key: string | null;
  }

  export type JSXElementConstructor<P> = (props: P) => ReactElement<any, any> | null;
  export type ReactPortal = ReactElement;

  export type FC<P = {}> = (props: P & { children?: ReactNode }) => ReactElement<any, any> | null;
  export type FunctionComponent<P = {}> = FC<P>;

  export type PropsWithChildren<P = unknown> = P & { children?: ReactNode | undefined };

  export type Dispatch<A> = (value: A) => void;
  export type SetStateAction<S> = S | ((prevState: S) => S);

  export function useState<S>(initialState: S | (() => S)): [S, Dispatch<SetStateAction<S>>];
  export function useState<S = undefined>(): [S | undefined, Dispatch<SetStateAction<S | undefined>>];

  export function useEffect(effect: () => void | (() => void), deps?: readonly any[]): void;
  export function useCallback<T extends (...args: any[]) => any>(callback: T, deps: readonly any[]): T;
  export function useMemo<T>(factory: () => T, deps: readonly any[] | undefined): T;
  export function useRef<T>(initialValue: T): { current: T };
  export function useRef<T = undefined>(initialValue?: T): { current: T };
  export function useContext<T>(context: Context<T>): T;

  export function forwardRef<T, P = {}>(
    render: (props: P, ref: React.Ref<T>) => ReactElement | null
  ): ForwardRefExoticComponent<PropsWithoutRef<P> & RefAttributes<T>>;

  export type Ref<T> = { current: T | null } | ((instance: T | null) => void) | null;
  export type PropsWithoutRef<P> = P;
  export interface RefAttributes<T> {
    ref?: Ref<T>;
  }
  export interface ForwardRefExoticComponent<P> extends FC<P> {
    defaultProps?: Partial<P>;
    displayName?: string;
  }

  export interface Context<T> {
    Provider: FC<{ value: T; children?: ReactNode }>;
    displayName?: string;
  }
  export function createContext<T>(defaultValue: T): Context<T>;

  export interface ChangeEvent<T = any> {
    target: T & { value: string };
  }
  export interface FormEvent<T = Element> {
    preventDefault: () => void;
    stopPropagation: () => void;
    target: T;
  }
  export interface MouseEvent<T = Element> {
    preventDefault: () => void;
    stopPropagation: () => void;
    target: T;
  }
  export interface KeyboardEvent<T = Element> {
    key: string;
    ctrlKey: boolean;
    metaKey: boolean;
    preventDefault: () => void;
  }

  export interface HTMLAttributes<T> {
    className?: string;
    style?: Record<string, any>;
    id?: string;
    role?: string;
    tabIndex?: number;
    onClick?: (e: MouseEvent<T>) => void;
    onKeyDown?: (e: KeyboardEvent<T>) => void;
    children?: ReactNode;
    title?: string;
    [key: string]: any;
  }

  export interface ButtonHTMLAttributes<T> extends HTMLAttributes<T> {
    type?: "button" | "submit" | "reset";
    disabled?: boolean;
    onClick?: (e: MouseEvent<T>) => void;
  }

  export interface InputHTMLAttributes<T> extends HTMLAttributes<T> {
    type?: string;
    value?: string | number | readonly string[];
    defaultValue?: string | number | readonly string[];
    placeholder?: string;
    disabled?: boolean;
    required?: boolean;
    autoFocus?: boolean;
    onChange?: (e: ChangeEvent<T>) => void;
    onFocus?: (e: any) => void;
    onBlur?: (e: any) => void;
  }

  export interface SelectHTMLAttributes<T> extends HTMLAttributes<T> {
    value?: string | number | readonly string[];
    defaultValue?: string | number | readonly string[];
    disabled?: boolean;
    required?: boolean;
    onChange?: (e: ChangeEvent<T>) => void;
  }

  export interface SVGProps<T> extends HTMLAttributes<T> {
    width?: string | number;
    height?: string | number;
    viewBox?: string;
    fill?: string;
    stroke?: string;
  }

  export interface AnchorHTMLAttributes<T> extends HTMLAttributes<T> {
    href?: string;
    target?: string;
    rel?: string;
  }
}

declare namespace JSX {
  interface Element extends React.ReactElement<any, any> {}
  interface IntrinsicElements {
    [elemName: string]: any;
  }
}

declare module "react" {
  export = React;
}

declare module "react-dom/client" {
  export function createRoot(container: Element | DocumentFragment): {
    render(children: React.ReactNode): void;
    unmount(): void;
  };
}

declare module "clsx" {
  export type ClassValue = string | number | boolean | undefined | null | { [key: string]: boolean | undefined | null } | ClassValue[];
  export function clsx(...inputs: ClassValue[]): string;
  export default clsx;
}

declare module "tailwind-merge" {
  export function twMerge(...classLists: (string | undefined | null | false)[]): string;
}

declare module "lucide-react" {
  import React from "react";
  export interface LucideProps extends React.SVGProps<SVGSVGElement> {
    size?: number | string;
    strokeWidth?: number | string;
    absoluteStrokeWidth?: boolean;
    color?: string;
  }
  export type Icon = React.FC<LucideProps>;
  export const LayoutDashboard: Icon;
  export const BarChart2: Icon;
  export const TrendingUp: Icon;
  export const TrendingDown: Icon;
  export const Brain: Icon;
  export const AlertTriangle: Icon;
  export const Activity: Icon;
  export const Briefcase: Icon;
  export const Bookmark: Icon;
  export const Newspaper: Icon;
  export const Settings: Icon;
  export const Sparkles: Icon;
  export const Zap: Icon;
  export const ArrowRight: Icon;
  export const ArrowUpRight: Icon;
  export const Search: Icon;
  export const Menu: Icon;
  export const User: Icon;
  export const LogOut: Icon;
  export const ShieldCheck: Icon;
  export const ShieldAlert: Icon;
  export const ChevronDown: Icon;
  export const Minus: Icon;
  export const X: Icon;
  export const Layers: Icon;
  export const AlertCircle: Icon;
  export const CheckCircle2: Icon;
  export const Info: Icon;
  export const Send: Icon;
  export const Database: Icon;
  export const FileText: Icon;
  export const Play: Icon;
  export const AlertOctagon: Icon;
  export const HelpCircle: Icon;
  export const Plus: Icon;
  export const ExternalLink: Icon;
  export const Globe: Icon;
  export const Key: Icon;
  export const Lock: Icon;
  export const Mail: Icon;
  export const Loader2: Icon;
  export const CornerDownLeft: Icon;
  export const Filter: Icon;
  export const RefreshCw: Icon;
  export const Shield: Icon;
  export const PieChart: Icon;
  export const Sliders: Icon;
  export const Share2: Icon;
  export const Network: Icon;
}

declare module "next" {
  export interface Metadata {
    title?: string | { default: string; template: string };
    description?: string;
    [key: string]: unknown;
  }
}

declare module "next/link" {
  import React from "react";
  export interface LinkProps extends React.AnchorHTMLAttributes<HTMLAnchorElement> {
    href: string;
    replace?: boolean;
    scroll?: boolean;
    prefetch?: boolean;
  }
  const Link: React.FC<LinkProps>;
  export default Link;
}

declare module "next/navigation" {
  export function useRouter(): {
    push: (url: string) => void;
    replace: (url: string) => void;
    back: () => void;
    forward: () => void;
    refresh: () => void;
    prefetch: (url: string) => void;
  };
  export function usePathname(): string;
  export function useParams(): Record<string, string | string[]>;
  export function useSearchParams(): URLSearchParams;
  export function redirect(url: string): never;
}

declare module "next/font/google" {
  export function Inter(options?: { subsets?: string[]; variable?: string; display?: string }): { variable: string; className: string };
  export function JetBrains_Mono(options?: { subsets?: string[]; variable?: string; display?: string }): { variable: string; className: string };
}

declare module "recharts" {
  import React from "react";
  export const ResponsiveContainer: React.FC<{ width?: string | number; height?: string | number; children?: React.ReactNode }>;
  export const AreaChart: React.FC<any>;
  export const Area: React.FC<any>;
  export const LineChart: React.FC<any>;
  export const Line: React.FC<any>;
  export const XAxis: React.FC<any>;
  export const YAxis: React.FC<any>;
  export const Tooltip: React.FC<any>;
  export const CartesianGrid: React.FC<any>;
  export const RadarChart: React.FC<any>;
  export const PolarGrid: React.FC<any>;
  export const PolarAngleAxis: React.FC<any>;
  export const PolarRadiusAxis: React.FC<any>;
  export const Radar: React.FC<any>;
  export const PieChart: React.FC<any>;
  export const Pie: React.FC<any>;
  export const Cell: React.FC<any>;
}

declare module "lightweight-charts" {
  export type UTCTimestamp = number & { __escaped?: never };
  export interface CandlestickData {
    time: UTCTimestamp;
    open: number;
    high: number;
    low: number;
    close: number;
  }
  export interface HistogramData {
    time: UTCTimestamp;
    value: number;
    color?: string;
  }
  export interface IChartApi {
    applyOptions: (options: any) => void;
    remove: () => void;
    addCandlestickSeries: (options?: any) => ISeriesApi<"Candlestick">;
    addHistogramSeries: (options?: any) => ISeriesApi<"Histogram">;
    timeScale: () => { fitContent: () => void };
  }
  export interface ISeriesApi<T> {
    setData: (data: any[]) => void;
    priceScale: () => { applyOptions: (options: any) => void };
  }
  export function createChart(container: HTMLElement, options?: any): IChartApi;
}

declare module "axios" {
  export interface AxiosRequestConfig {
    url?: string;
    method?: string;
    baseURL?: string;
    headers?: Record<string, string>;
    params?: any;
    data?: any;
    timeout?: number;
  }
  export interface InternalAxiosRequestConfig extends AxiosRequestConfig {
    headers: any;
  }
  export interface AxiosResponse<T = any> {
    data: T;
    status: number;
    statusText: string;
    headers: any;
    config: AxiosRequestConfig;
  }
  export interface AxiosError<T = any> extends Error {
    config?: AxiosRequestConfig;
    code?: string;
    request?: any;
    response?: AxiosResponse<T>;
    isAxiosError: boolean;
  }
  export interface AxiosInstance {
    <T = any>(config: AxiosRequestConfig): Promise<AxiosResponse<T>>;
    get<T = any>(url: string, config?: AxiosRequestConfig): Promise<AxiosResponse<T>>;
    delete<T = any>(url: string, config?: AxiosRequestConfig): Promise<AxiosResponse<T>>;
    post<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<AxiosResponse<T>>;
    put<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<AxiosResponse<T>>;
    patch<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<AxiosResponse<T>>;
    interceptors: {
      request: {
        use: (onFulfilled?: (value: InternalAxiosRequestConfig) => InternalAxiosRequestConfig | Promise<InternalAxiosRequestConfig>, onRejected?: (error: any) => any) => number;
      };
      response: {
        use: (onFulfilled?: (value: AxiosResponse) => AxiosResponse | Promise<AxiosResponse>, onRejected?: (error: any) => any) => number;
      };
    };
  }
  const axios: {
    create: (config?: AxiosRequestConfig) => AxiosInstance;
  };
  export default axios;
}

declare module "tailwindcss" {
  export interface Config {
    content: string[];
    theme?: any;
    plugins?: any[];
  }
}

declare namespace NodeJS {
  interface ProcessEnv {
    NEXT_PUBLIC_API_URL?: string;
    [key: string]: string | undefined;
  }
  interface Process {
    env: ProcessEnv;
  }
}

declare var process: NodeJS.Process;
