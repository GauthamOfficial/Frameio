"use client"

import * as React from "react"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { ChevronUp, ChevronDown, ChevronsUpDown } from "lucide-react"

interface TableProps {
  children: React.ReactNode
  className?: string
}

interface TableHeaderProps {
  children: React.ReactNode
  className?: string
}

interface TableBodyProps {
  children: React.ReactNode
  className?: string
}

interface TableRowProps {
  children: React.ReactNode
  className?: string
  onClick?: () => void
  hover?: boolean
}

interface TableHeadProps {
  children: React.ReactNode
  className?: string
  sortable?: boolean
  sortDirection?: "asc" | "desc" | null
  onSort?: () => void
}

interface TableCellProps {
  children: React.ReactNode
  className?: string
}

interface SortableTableHeadProps {
  children: React.ReactNode
  className?: string
  sortKey: string
  currentSort?: {
    key: string
    direction: "asc" | "desc"
  }
  onSort: (key: string) => void
}

interface PaginationProps {
  currentPage: number
  totalPages: number
  onPageChange: (page: number) => void
  showPageNumbers?: boolean
  maxVisiblePages?: number
}

// Base Table Components
const Table: React.FC<TableProps> = ({ children, className }) => (
  <div className="relative overflow-x-auto">
    <table className={cn("w-full caption-bottom text-sm", className)}>
      {children}
    </table>
  </div>
)

const TableHeader: React.FC<TableHeaderProps> = ({ children, className }) => (
  <thead className={cn("[&_tr]:border-b", className)}>
    {children}
  </thead>
)

const TableBody: React.FC<TableBodyProps> = ({ children, className }) => (
  <tbody className={cn("[&_tr:last-child]:border-0", className)}>
    {children}
  </tbody>
)

const TableRow: React.FC<TableRowProps> = ({ 
  children, 
  className, 
  onClick, 
  hover = true 
}) => (
  <tr
    className={cn(
      "border-b transition-colors hover:bg-muted/50 data-[state=selected]:bg-muted",
      hover && "cursor-pointer",
      className
    )}
    onClick={onClick}
  >
    {children}
  </tr>
)

const TableHead: React.FC<TableHeadProps> = ({ 
  children, 
  className, 
  sortable = false,
  sortDirection,
  onSort 
}) => (
  <th
    className={cn(
      "h-12 px-4 text-left align-middle font-medium text-muted-foreground [&:has([role=checkbox])]:pr-0",
      sortable && "cursor-pointer select-none hover:text-foreground",
      className
    )}
    onClick={sortable ? onSort : undefined}
  >
    <div className="flex items-center space-x-2">
      <span>{children}</span>
      {sortable && (
        <div className="flex flex-col">
          {sortDirection === "asc" ? (
            <ChevronUp className="h-4 w-4" />
          ) : sortDirection === "desc" ? (
            <ChevronDown className="h-4 w-4" />
          ) : (
            <ChevronsUpDown className="h-4 w-4 opacity-50" />
          )}
        </div>
      )}
    </div>
  </th>
)

const TableCell: React.FC<TableCellProps> = ({ children, className }) => (
  <td className={cn("p-4 align-middle [&:has([role=checkbox])]:pr-0", className)}>
    {children}
  </td>
)

// Sortable Table Head Component
const SortableTableHead: React.FC<SortableTableHeadProps> = ({
  children,
  className,
  sortKey,
  currentSort,
  onSort,
}) => {
  const sortDirection = currentSort?.key === sortKey ? currentSort.direction : null

  return (
    <TableHead
      className={className}
      sortable
      sortDirection={sortDirection}
      onSort={() => onSort(sortKey)}
    >
      {children}
    </TableHead>
  )
}

// Pagination Component
const Pagination: React.FC<PaginationProps> = ({
  currentPage,
  totalPages,
  onPageChange,
  showPageNumbers = true,
  maxVisiblePages = 5,
}) => {
  const getVisiblePages = () => {
    const pages: (number | string)[] = []
    const halfVisible = Math.floor(maxVisiblePages / 2)
    
    let startPage = Math.max(1, currentPage - halfVisible)
    let endPage = Math.min(totalPages, currentPage + halfVisible)
    
    // Adjust if we're near the beginning or end
    if (endPage - startPage + 1 < maxVisiblePages) {
      if (startPage === 1) {
        endPage = Math.min(totalPages, startPage + maxVisiblePages - 1)
      } else {
        startPage = Math.max(1, endPage - maxVisiblePages + 1)
      }
    }
    
    // Add first page and ellipsis if needed
    if (startPage > 1) {
      pages.push(1)
      if (startPage > 2) {
        pages.push("...")
      }
    }
    
    // Add visible pages
    for (let i = startPage; i <= endPage; i++) {
      pages.push(i)
    }
    
    // Add ellipsis and last page if needed
    if (endPage < totalPages) {
      if (endPage < totalPages - 1) {
        pages.push("...")
      }
      pages.push(totalPages)
    }
    
    return pages
  }

  const visiblePages = getVisiblePages()

  return (
    <div className="flex items-center justify-between px-2">
      <div className="flex-1 text-sm text-muted-foreground">
        Page {currentPage} of {totalPages}
      </div>
      
      <div className="flex items-center space-x-2">
        <Button
          variant="outline"
          size="sm"
          onClick={() => onPageChange(currentPage - 1)}
          disabled={currentPage === 1}
        >
          Previous
        </Button>
        
        {showPageNumbers && (
          <div className="flex items-center space-x-1">
            {visiblePages.map((page, index) => (
              <React.Fragment key={index}>
                {page === "..." ? (
                  <span className="px-2 text-muted-foreground">...</span>
                ) : (
                  <Button
                    variant={currentPage === page ? "default" : "outline"}
                    size="sm"
                    onClick={() => onPageChange(page as number)}
                    className="w-8 h-8 p-0"
                  >
                    {page}
                  </Button>
                )}
              </React.Fragment>
            ))}
          </div>
        )}
        
        <Button
          variant="outline"
          size="sm"
          onClick={() => onPageChange(currentPage + 1)}
          disabled={currentPage === totalPages}
        >
          Next
        </Button>
      </div>
    </div>
  )
}

// Data Table Hook for sorting and pagination
interface UseDataTableProps<T> {
  data: T[]
  initialSort?: {
    key: keyof T
    direction: "asc" | "desc"
  }
  initialPageSize?: number
}

function useDataTable<T>({
  data,
  initialSort,
  initialPageSize = 10,
}: UseDataTableProps<T>) {
  const [sort, setSort] = React.useState(initialSort)
  const [currentPage, setCurrentPage] = React.useState(1)
  const [pageSize, setPageSize] = React.useState(initialPageSize)

  const sortedData = React.useMemo(() => {
    if (!sort) return data

    return [...data].sort((a, b) => {
      const aValue = a[sort.key]
      const bValue = b[sort.key]

      if (aValue < bValue) return sort.direction === "asc" ? -1 : 1
      if (aValue > bValue) return sort.direction === "asc" ? 1 : -1
      return 0
    })
  }, [data, sort])

  const paginatedData = React.useMemo(() => {
    const startIndex = (currentPage - 1) * pageSize
    const endIndex = startIndex + pageSize
    return sortedData.slice(startIndex, endIndex)
  }, [sortedData, currentPage, pageSize])

  const totalPages = Math.ceil(sortedData.length / pageSize)

  const handleSort = (key: keyof T) => {
    setSort(prevSort => {
      if (prevSort?.key === key) {
        return {
          key,
          direction: prevSort.direction === "asc" ? "desc" : "asc",
        }
      }
      return { key, direction: "asc" }
    })
    setCurrentPage(1) // Reset to first page when sorting
  }

  const handlePageChange = (page: number) => {
    setCurrentPage(page)
  }

  return {
    data: paginatedData,
    sort,
    currentPage,
    pageSize,
    totalPages,
    totalItems: data.length,
    handleSort,
    handlePageChange,
    setPageSize,
  }
}

export {
  Table,
  TableHeader,
  TableBody,
  TableRow,
  TableHead,
  TableCell,
  SortableTableHead,
  Pagination,
  useDataTable,
}
