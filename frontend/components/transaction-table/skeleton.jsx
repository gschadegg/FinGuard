import { TableCell, TableRow } from '@/components/ui/table'
import { Skeleton } from '@/components/ui/skeleton'

const TableSkeleton = ({ colSpan }) => {
  return (
    <>
      <TableRow data-testid="table-skeleton">
        <TableCell colSpan={colSpan} className="h-2 text-center">
          <Skeleton className="h-10 w-full" />
        </TableCell>
      </TableRow>
      <TableRow>
        <TableCell colSpan={colSpan} className="h-2 text-center">
          <Skeleton className="h-10 w-full" />
        </TableCell>
      </TableRow>
      <TableRow>
        <TableCell colSpan={colSpan} className="h-2 text-center">
          <Skeleton className="h-10 w-full" />
        </TableCell>
      </TableRow>
      <TableRow>
        <TableCell colSpan={colSpan} className="h-2 text-center">
          <Skeleton className="h-10 w-full" />
        </TableCell>
      </TableRow>
      <TableRow>
        <TableCell colSpan={colSpan} className="h-2 text-center">
          <Skeleton className="h-10 w-full" />
        </TableCell>
      </TableRow>
    </>
  )
}

export default TableSkeleton
