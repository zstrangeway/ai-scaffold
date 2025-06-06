// Styles
import "./styles/globals.css"

// Components
export { Button, type ButtonProps } from "./components/button"
export { 
  Card, 
  CardHeader, 
  CardFooter, 
  CardTitle, 
  CardDescription, 
  CardContent 
} from "./components/card"
export { Input, type InputProps } from "./components/input"

// New shadcn UI components
export {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "./components/ui/accordion"

export { Alert, AlertDescription, AlertTitle } from "./components/ui/alert"

export {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "./components/ui/alert-dialog"

export { AspectRatio } from "./components/ui/aspect-ratio"

export { Avatar, AvatarFallback, AvatarImage } from "./components/ui/avatar"

export { Badge, type BadgeProps } from "./components/ui/badge"

export {
  Breadcrumb,
  BreadcrumbEllipsis,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from "./components/ui/breadcrumb"

export { Calendar } from "./components/ui/calendar"

export {
  Carousel,
  CarouselContent,
  CarouselItem,
  CarouselNext,
  CarouselPrevious,
  type CarouselApi,
} from "./components/ui/carousel"

export {
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
  ChartLegend,
  ChartLegendContent,
  type ChartConfig,
} from "./components/ui/chart"

export { Checkbox } from "./components/ui/checkbox"

export {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "./components/ui/collapsible"

export {
  Command,
  CommandDialog,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
  CommandSeparator,
  CommandShortcut,
} from "./components/ui/command"

export {
  ContextMenu,
  ContextMenuCheckboxItem,
  ContextMenuContent,
  ContextMenuItem,
  ContextMenuLabel,
  ContextMenuRadioGroup,
  ContextMenuRadioItem,
  ContextMenuSeparator,
  ContextMenuShortcut,
  ContextMenuSub,
  ContextMenuSubContent,
  ContextMenuSubTrigger,
  ContextMenuTrigger,
} from "./components/ui/context-menu"

// Additional components from main branch
export { DatePicker } from "./components/ui/date-picker"

export { 
  Dialog,
  DialogPortal,
  DialogOverlay,
  DialogTrigger,
  DialogClose,
  DialogContent,
  DialogHeader,
  DialogFooter,
  DialogTitle,
  DialogDescription
} from "./components/ui/dialog"

export {
  Drawer,
  DrawerPortal,
  DrawerOverlay,
  DrawerTrigger,
  DrawerClose,
  DrawerContent,
  DrawerHeader,
  DrawerFooter,
  DrawerTitle,
  DrawerDescription
} from "./components/ui/drawer"

export {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuCheckboxItem,
  DropdownMenuRadioItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuShortcut,
  DropdownMenuGroup,
  DropdownMenuPortal,
  DropdownMenuSub,
  DropdownMenuSubContent,
  DropdownMenuSubTrigger,
  DropdownMenuRadioGroup
} from "./components/ui/dropdown-menu"

export {
  HoverCard,
  HoverCardTrigger,
  HoverCardContent
} from "./components/ui/hover-card"

export {
  InputOTP,
  InputOTPGroup,
  InputOTPSeparator,
  InputOTPSlot
} from "./components/ui/input-otp"

export { Label } from "./components/ui/label"

export {
  Menubar,
  MenubarMenu,
  MenubarTrigger,
  MenubarContent,
  MenubarItem,
  MenubarSeparator,
  MenubarLabel,
  MenubarCheckboxItem,
  MenubarRadioGroup,
  MenubarRadioItem,
  MenubarPortal,
  MenubarSubContent,
  MenubarSubTrigger,
  MenubarGroup,
  MenubarSub,
  MenubarShortcut
} from "./components/ui/menubar"

export {
  NavigationMenu,
  NavigationMenuList,
  NavigationMenuItem,
  NavigationMenuContent,
  NavigationMenuTrigger,
  NavigationMenuLink,
  NavigationMenuIndicator,
  NavigationMenuViewport,
  navigationMenuTriggerStyle
} from "./components/ui/navigation-menu"

export {
  Pagination,
  PaginationContent,
  PaginationEllipsis,
  PaginationItem,
  PaginationLink,
  PaginationNext,
  PaginationPrevious
} from "./components/ui/pagination"

export {
  Popover,
  PopoverTrigger,
  PopoverContent
} from "./components/ui/popover"

export { Progress } from "./components/ui/progress"

// Components added in this PR
export { 
  ResizablePanelGroup,
  ResizablePanel,
  ResizableHandle 
} from "./components/ui/resizable"

export { ScrollArea, ScrollBar } from "./components/ui/scroll-area"

export { 
  Select,
  SelectGroup,
  SelectValue,
  SelectTrigger,
  SelectContent,
  SelectLabel,
  SelectItem,
  SelectSeparator,
  SelectScrollUpButton,
  SelectScrollDownButton
} from "./components/ui/select"

export { Separator } from "./components/ui/separator"

export {
  Sheet,
  SheetPortal,
  SheetOverlay,
  SheetTrigger,
  SheetClose,
  SheetContent,
  SheetHeader,
  SheetFooter,
  SheetTitle,
  SheetDescription
} from "./components/ui/sheet"

export {
  Sidebar,
  SidebarProvider,
  SidebarTrigger,
  SidebarInset,
  SidebarInput,
  SidebarHeader,
  SidebarFooter,
  SidebarContent,
  SidebarGroup,
  SidebarGroupLabel,
  SidebarGroupContent,
  SidebarGroupAction,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarMenuAction,
  SidebarMenuBadge,
  SidebarMenuSkeleton,
  SidebarMenuSub,
  SidebarMenuSubButton,
  SidebarMenuSubItem,
  SidebarRail,
  useSidebar
} from "./components/ui/sidebar"

export { Skeleton } from "./components/ui/skeleton"

export { Slider } from "./components/ui/slider"

export { Toaster } from "./components/ui/sonner"

export { Switch } from "./components/ui/switch"

export {
  Table,
  TableHeader,
  TableBody,
  TableFooter,
  TableHead,
  TableRow,
  TableCell,
  TableCaption
} from "./components/ui/table"

export {
  Tabs,
  TabsList,
  TabsTrigger,
  TabsContent
} from "./components/ui/tabs"

export { Textarea } from "./components/ui/textarea"

export {
  type ToastProps,
  type ToastActionElement,
  ToastProvider,
  ToastViewport,
  Toast,
  ToastTitle,
  ToastDescription,
  ToastClose,
  ToastAction
} from "./components/ui/toast"

export { Toaster as ToastToaster } from "./components/ui/toaster"

export { Toggle, toggleVariants } from "./components/ui/toggle"

export { ToggleGroup, ToggleGroupItem } from "./components/ui/toggle-group"

export {
  Tooltip,
  TooltipTrigger,
  TooltipContent,
  TooltipProvider
} from "./components/ui/tooltip"

// Third-party libraries
export * from "react-hook-form"

// Hooks
export { useToast, toast } from "./hooks/use-toast"
export { useIsMobile } from "./hooks/use-mobile"

// Utilities
export { cn } from "./lib/utils"